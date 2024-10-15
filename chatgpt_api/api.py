import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json

# Set up OpenAI client with API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
print(f"Loaded OpenAI API key: {client.api_key}")

app = FastAPI()

class Query(BaseModel):
    question: str

# Load the schema from the JSON file
def load_schema_from_json(file_path):
    try:
        with open(file_path, 'r') as f:
            schema = json.load(f)
        return schema
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Schema file not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON schema.")

# Path to your JSON schema file
SCHEMA_FILE = 'chatgpt_api/nport_metadata.json'

# Load the schema
db_schema = load_schema_from_json(SCHEMA_FILE)

# Format the schema for GPT
def format_schema_for_gpt(schema):
    formatted_schema = ""

    for table in schema.get('tables', []):
        table_name = table['url'].replace('.tsv', '')  # Use the table name without .tsv
        columns = table['tableSchema']['columns']
        column_list = ", ".join([f"{col['name']} {col['datatype']['base'].upper()}" for col in columns])
        formatted_schema += f"{table_name}: {column_list}\n"

    return formatted_schema

schema_info = format_schema_for_gpt(db_schema)

# LLM prompting for SQL generation
def generate_sql(question: str) -> str:
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

    chat_completion = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that generates SQL queries based on natural language questions about financial data."
        },
        {"role": "user", "content": prompt}
    ])

    return chat_completion.choices[0].message.content.strip()

# Database SQL Retrieval
def execute_sql(query: str) -> list:
    try:
        conn = sqlite3.connect('financial_data.db')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
    except sqlite3.Error as e:
        # Return the error message instead of raising an exception
        return [f"Database error: {str(e)}"]
    finally:
        conn.close()
    return results

# Frontend HTTP access point
@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/query")
async def process_query(query: Query):
    sql_query = generate_sql(query.question)
    results = sql_query ## REPLACE LATER WITH execute_sql(sql_query)
    return {"sql_query": sql_query, "results": results}

@app.get("/schema-raw")
async def get_raw_schema():
    # Return the raw schema without any formatting
    return db_schema

@app.get("/schema")
async def get_schema():
    return {"schema": format_schema_for_gpt(db_schema)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
