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
    
# Path to your JSON schema files
SCHEMA_FILE = 'chatgpt_api/nport_metadata.json'

try:
    db_schema = load_schema_from_json(SCHEMA_FILE)
except Exception as e:
    logger.error(f"Failed to load initial schema: {str(e)}")
    db_schema = None


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

    schema_info = format_schema_for_gpt(db_schema)
    prompt = get_prompt()
    prompt = f"""
    ---
    OVERALL TASK:
    I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question.
    ---
    ---
    DATABASE SCHEMA:
    Given the following database schema:
    {schema_info}

    Generate an SQL query that retrieves from the database the answer to this question:
    Question: {question}
    ---
    ---
    OUTPUT FORMAT SPECIFICATION:
    The answer output must be only text of the SQL query that satisfies what the question asks, without any extra text or description.
    ---
    ---
    EXAMPLES:
        Example 1: 
        Question: i want accession number of 20 entries in SUBMISSION table
        Answer: SELECT accession_number FROM SUBMISSION
    ---
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates SQL queries based on natural language questions about financial data."
                },
                {"role": "user", "content": prompt}
            ]
        )
        sql_query = response.choices[0].message.content.strip()
        logger.info(f"Generated SQL query: {sql_query}")
        return sql_query
    except openai.APIStatusError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )
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
        conn = sqlite3.connect('financial_data.db')
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

# Frontend HTTP access point
@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/query")
async def process_query(query: Query):
    logger.info(f"Processing query: {query.question}")
    try:
        sql_query = generate_sql(query.question)
        csv_results = execute_sql(sql_query)
        
        return StreamingResponse(
            io.StringIO(csv_results),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=results.csv"}
        )
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
