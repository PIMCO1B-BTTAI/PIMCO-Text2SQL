from openai import OpenAI
import json
import sqlite3
import csv
import io
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from typing import Optional
#from chatgpt_api.chat_prompt import generate_sql_and_reasoning

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not configured")

logger.info("OpenAI API key loaded successfully")

app = FastAPI()

class Query(BaseModel):
    question: str

def load_schema_from_json(file_path: str) -> dict:
    logger.debug(f"Attempting to load schema from {file_path}")
    try:
        with open(file_path, 'r') as f:
            schema = json.load(f)
        logger.info("Schema loaded successfully")
        return schema
    except FileNotFoundError:
        logger.error(f"Schema file not found at {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Schema file not found at {file_path}"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error decoding JSON schema: {str(e)}"
        )


def format_schema_for_gpt(schema: dict) -> str:
    try:
        formatted_schema = ""
        for table in schema.get('tables', []):
            table_name = table['url'].replace('.tsv', '')
            columns = table['tableSchema']['columns']
            column_list = ", ".join([
                f"{col['name']} {col['datatype']['base'].upper()}"
                for col in columns
            ])
            formatted_schema += f"{table_name}: {column_list}\n"
        return formatted_schema
    except Exception as e:
        logger.error(f"Error formatting schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error formatting schema: {str(e)}"
        )


# Path to the JSON schema file
SCHEMA_FILE = 'chatgpt_api/schema.json'
print(f"Expected schema path: {SCHEMA_FILE}")  # Add this line to see the path in logs

try:
    db_schema = load_schema_from_json(SCHEMA_FILE)
except Exception as e:
    logger.error(f"Failed to load initial schema: {str(e)}")
    db_schema = None

schema_info = format_schema_for_gpt(db_schema) 


def get_prompt() -> str:
    try:
        from . import chat_prompt
        return chat_prompt.full_prompt
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to load chat prompt: {str(e)}")
        return ""
    

# LLM prompting for SQL generation
def generate_sql(question: str) -> str:
    logger.debug(f"Generating SQL for question: {question}")
    
    if not db_schema:
        logger.error("Database schema not loaded")
        raise HTTPException(
            status_code=500,
            detail="Database schema not loaded"
        )

    #schema_info = format_schema_for_gpt(db_schema) #This is currently unused
    prompt = f"""
    ```
    OVERALL TASK:
    I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question: {question}
    ```
    """ + get_prompt()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial database assistant that generates SQL queries based on natural language questions about financial data."
                },# adding tools parameter and pass schema for reasoning
                {"role": "user", "content": prompt}
            ],
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "sql_query",
                        "description": "Execute SQL queries against the database schema which includes tables like FUND_REPORTED_INFO (containing SERIES_NAME, TOTAL_ASSETS) and REGISTRANT (containing REGISTRANT_NAME). Use these tables to analyze fund data.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The SQL query to execute. Example: To find top PIMCO funds, use: SELECT SERIES_NAME, TOTAL_ASSETS FROM FUND_REPORTED_INFO JOIN REGISTRANT ON FUND_REPORTED_INFO.ACCESSION_NUMBER = REGISTRANT.ACCESSION_NUMBER WHERE REGISTRANT_NAME LIKE '%PIMCO%' ORDER BY TOTAL_ASSETS DESC LIMIT 5"
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    "schema": schema_info # this is where the schema is entered
                }
            ], 
        tool_choice={"type": "function", "function": {"name": "sql_query"}}  # force the model to use the SQL function
        )

        function_call = response.choices[0].message.tool_calls[0].function
        if function_call.name == "sql_query":
            # openai returns function arguments as a JSON string, so we need to parse it
            # The query will be in the "query" field of the parsed JSON
            sql_query = json.loads(function_call.arguments)["query"]
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
        else:
            raise ValueError(f"Unexpected function call: {function_call.name}")

    except Exception as e:
        logger.error(f"Unexpected error generating SQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL: {str(e)}"
    )

def execute_sql(query: str) -> str:
    logger.debug(f"Executing SQL query: {query}")
    conn = None
    try:
        conn = sqlite3.connect('sqlite/nport.db')
        cursor = conn.cursor()

        # Execute the query with a timeout
        cursor.execute(query)

        # Fetch column names and rows
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Convert the results to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        csv_data = output.getvalue()
        output.close()

        logger.info("SQL query executed successfully")
        return csv_data
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error executing SQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing SQL: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


def get_column_mapping(db_sql: str, gpt_sql: str) -> dict:
    """
    Uses GPT to generate a mapping between two SQL queries' columns
    
    db_sql (str): The SQL query that actually runs on the database
    gpt_sql (str): The SQL query generated by GPT
    
    Returns mapping of database columns to GPT columns
    """

    prompt = f"""Given these two SQL queries, create a JSON mapping of column names from Query 1 to Query 2:

    Query 1 (Database): {db_sql}
    Query 2 (Generated): {gpt_sql}
    
    Return only a JSON mapping where keys are column names from Query 1 and values are corresponding column names from Query 2.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a SQL expert that creates column mappings between queries."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        mapping = json.loads(response.choices[0].message.content)
        logger.info(f"Generated column mapping: {mapping}")
        return mapping
        
    except Exception as e:
        logger.error(f"Error generating column mapping: {str(e)}")
        return {}


# Frontend HTTP access point
@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/query")
async def process_query(query: Query):
    logger.info(f"Processing query: {query.question}")
    try:
        sql_query = generate_sql(query.question)
        logger.info(f"Processing query: {query.question}")
        csv_results = execute_sql(sql_query)
        return {
            "sql_query": sql_query,
            "csv_results": csv_results  # CSV data embedded as a JSON field
        }
        #return StreamingResponse(
        #    io.StringIO(csv_results),
        #    media_type="text/csv",
        #    headers={"Content-Disposition": "attachment; filename=results.csv"}
        #)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/schema-raw")
async def get_raw_schema():
    # Return the raw schema without any formatting
    return db_schema

@app.get("/schema")
async def get_schema():
    if not db_schema:
        raise HTTPException(
            status_code=500,
            detail="Schema not loaded"
        )
    return {"schema": format_schema_for_gpt(db_schema)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
