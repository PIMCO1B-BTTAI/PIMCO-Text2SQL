import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# Set up OpenAI client with API key
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()

class Query(BaseModel):
    question: str

# LLM prompting for SQL generation
def generate_sql(question: str) -> str:
    schema_info = """
    Tables:
    1. fund_info (id, fund_name, manager, inception_date)
    2. holdings (fund_id, security_name, quantity, market_value)
    3. performance (fund_id, date, return)
    """
    prompt = f"""
    Given the following database schema:
    {schema_info}

    Generate an SQL query to answer this question:
    Question: {question}
    SQL Query:
    """

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates SQL queries based on natural language questions about financial data."
            },
            {"role": "user", "content": prompt}
        ],
    )

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
@app.post("/query")
async def process_query(query: Query):
    sql_query = generate_sql(query.question)
    results = execute_sql(sql_query)
    return {"sql_query": sql_query, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
