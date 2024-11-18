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
from . import chat_prompt
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

from typing import Dict, List, Tuple
from Levenshtein import distance
from datasketch import MinHash, MinHashLSH
############################################ VALUE RETRIEVAL

class ValueRetriever:
    def __init__(self, schema_path: str = 'chatgpt_api/schema.json'):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Load schema
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Initialize LSH - locality sensitive hashing
        self.lsh = MinHashLSH(threshold=0.5, num_perm=128)
        self.minhashes = {}
        
        # Build LSH index from schema
        self._build_lsh_index()
        
    def _build_lsh_index(self):
        # Build lsh from the schema columns
        for table in self.schema.get('tables', []):
            table_schema = table.get('tableSchema', {})
            
            for column in table_schema.get('columns', []):
                word = column['name'].lower()
                minhash = MinHash(num_perm=128)
                
                for i in range(len(word) - 2):
                    minhash.update(word[i:i+3].encode('utf-8'))
                
                self.minhashes[word] = minhash
                self.lsh.insert(word, minhash)

    def find_similar_words(self, word: str) -> List[Tuple[str, float]]:
        # This is called after LLM performs keyword extraction
        word = word.lower()
        
        query_minhash = MinHash(num_perm=128)
        for i in range(len(word) - 2):
            query_minhash.update(word[i:i+3].encode('utf-8'))
        
        candidates = self.lsh.query(query_minhash)
        
        similarities = []
        for candidate in candidates:
            sim = 1 - distance(word, candidate) / max(len(word), len(candidate))
            if sim > 0.5:  # Similarity threshold here
                similarities.append((candidate, sim))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True) # Ranking of similar words in schema

    def extract_keywords(self, question: str) -> Dict:
        system_prompt = """You are an expert financial data analyst specializing in natural language understanding.
        Your task is to analyze questions about financial data and extract key components that will help in database queries.

        Objective: Break down the given question into essential components that will help formulate a database query.

        Instructions:
        1. Read the question carefully to identify:
        - Individual keywords that map to database columns or values
        - Technical terms related to financial data
        - Named entities (companies, funds, locations)
        - Numerical thresholds or values

        2. For each identified element, categorize it as:
        - keywords: Individual significant words that might match database columns
        - keyphrases: Multi-word expressions that represent single concepts
        - named_entities: Specific names of companies, funds, or locations
        - numerical_values: Any numbers, amounts, or thresholds

        3. Return only a JSON object with these categories, no explanation needed."""

        few_shot_examples = """
        Example Question: "Show me BlackRock funds with total assets over 1 billion managed in New York"
        {
            "keywords": ["funds", "assets", "managed"],
            "keyphrases": ["total assets"],
            "named_entities": ["BlackRock", "New York"],
            "numerical_values": ["1 billion"]
        }

        Example Question: "List all registrants with more than 10 mutual funds and net assets above 500M"
        {
            "keywords": ["registrants", "funds", "assets"],
            "keyphrases": ["mutual funds", "net assets"],
            "named_entities": [],
            "numerical_values": ["10", "500M"]
        }

        Example Question: "Which PIMCO funds were registered between 2020 and 2023 with California addresses?"
        {
            "keywords": ["funds", "registered", "addresses"],
            "keyphrases": ["PIMCO funds"],
            "named_entities": ["PIMCO", "California"],
            "numerical_values": ["2020", "2023"]
        }"""

        user_prompt = f"""Analyze this financial question and extract key components:

        Question: "{question}"

        Return a JSON object with the extracted components following the same format as the examples."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": few_shot_examples + "\n" + user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def process_question(self, question: str) -> Dict:
        # Extract keywords using LLM
        extracted_info = self.extract_keywords(question)
        
        # Find similar words using LSH we did on database schema
        similar_matches = {}
        
        # Process individual keywords
        for keyword in extracted_info['keywords']:
            similar_matches[keyword] = self.find_similar_words(keyword)
        
        # Process words in keyphrases
        for keyphrase in extracted_info['keyphrases']:
            words = keyphrase.split()
            for word in words:
                if word not in similar_matches:
                    similar_matches[word] = self.find_similar_words(word)
        
        return {
            "extracted_info": extracted_info,
            "similar_matches": similar_matches
        }


############################################ CLASSIFICATION

classification_prompt = '''Q: "Find the filing date and submission number of all reports filed for an NPORT-P submission."
schema_links: [submission.filing_date, submission.sub_type = "NPORT-P", submission.accession_number]
A: Let’s think step by step. The SQL query for the question "Find the filing date and submission number of all reports filed for an NPORT-P submission." needs these tables = [submission], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""]. 
So, we don't need JOIN and don't need nested queries, then the SQL query can be classified as "EASY".
Label: "EASY"

Q: "Get the names and CIK of registrants who are located in California."
schema_links: [registrant.registrant_name, registrant.cik, registrant.state = "US-CA"]
A: Let’s think step by step. The SQL query for the question "Get the names and CIK of registrants who are located in California." needs these tables = [registrant], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""]. 
So, we don't need JOIN and don't need nested queries, then the SQL query can be classified as "EASY".
Label: "EASY"

Q: "Find the names and CIK of registrants in California, but only for those whose total assets are above 100 million."
schema_links: [registrant.registrant_name, registrant.cik, registrant.state = "US-CA", fund_reported_info.total_assets > 100000000]
A: Let's analyze this. The query involves data from two tables: "registrant" for registrant details and "fund_reported_info" for total assets. Since we need to check if total assets exceed 100 million, a nested query is necessary to filter based on this condition. This is a nested query. So, the SQL query can be classified as "NESTED."
Label: "NESTED"

'''

def classification_prompt_maker(question,relevant_schema_links):
  instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
  instruction += "\nif need nested queries: predict NESTED\n"
  instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
  instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
  prompt = instruction + classification_prompt + 'Q: "' + question + '\nrelevant_schema_links: ' + relevant_schema_links + '\nA: Let’s think step by step.'
  return prompt

def process_question_classification(question,relevant_schema_links):
	classification = None
	while classification is None:
			try:
					classification = client.chat.completions.create(
						model="gpt-4o",
						messages=[{"role": "user", "content": classification_prompt_maker(question, relevant_schema_links=relevant_schema_links)}],
						n = 1,
						stream = False,
						temperature=0.0,
						max_tokens=600,
						top_p = 1.0,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						stop = ["Q:"]
					).choices[0].message.content
			except:
					time.sleep(3)
					pass
	try:
			predicted_class = classification.split("Label: ")[1]
	except:
			print("Slicing error for the classification module")
			predicted_class = '"NESTED"'
	return predicted_class
############################################ SQL GENERATION
easy_prompt = '''Q: "Find the issuers with a balance greater than 1 million."
Schema_links: [fund_reported_holding.balance]
SQL: SELECT DISTINCT issuer_name 
      FROM fund_reported_holding 
      WHERE balance > 1000000
'''

medium_prompt = '''Q: "Find the total upfront payments and receipts for swaps with fixed rate receipts."
Schema_links: [nonforeign_exchange_swap.upfront_payment, nonforeign_exchange_swap.upfront_receipt, nonforeign_exchange_swap.fixed_rate_receipt]
A: Let’s think step by step. For creating the SQL for the given question, we need to filter the swaps that have fixed rate receipts. Then, sum up the upfront payments and receipts. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: 
SELECT SUM(nonforeign_exchange_swap.upfront_payment) + SUM(nonforeign_exchange_swap.upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE nonforeign_exchange_swap.fixed_rate_receipt IS NOT NULL
SQL: 
SELECT SUM(upfront_payment) + SUM(upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE fixed_rate_receipt IS NOT NULL
'''

hard_prompt = '''Q: "Find the borrowers with aggregate value greater than $1 million and whose interest rate change at 10-year maturity for a 100 basis point change is positive."
Schema_links: [borrower.aggregate_value, borrower.name, interest_rate_risk.intrst_rate_change_10yr_dv100]
A: Let's think step by step. First, we need to filter borrowers with aggregate values greater than $1 million. Then, we need to check for interest rate changes at 10-year maturity where the change is positive. 
The SQL query for the sub-question "What are the borrowers with aggregate value greater than $1 million and positive interest rate change at 10-year maturity for 100 basis points?" is:

Intermediate_representation: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0

SQL: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0
'''

def hard_prompt_maker(question,database,schema_links,sub_questions=""):
    instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
    if sub_questions=="":
        stepping = f'''\nA: Let's think step by step. "{question}" can be solved by first solving a sub-question using nested queries".'''
    else:
        stepping = f'''\nA: Let's think step by step. "{question}" can be solved by first solving the answer to the following sub-question "{sub_questions}".'''
    prompt = instruction + hard_prompt+ chat_prompt.gpt_queries_hard+ 'Q: "' + question + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question:"'
    return prompt

def medium_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
    prompt = instruction + medium_prompt + chat_prompt.gpt_queries_medium+ 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
    return prompt

def easy_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
    prompt = instruction + easy_prompt + chat_prompt.gpt_queries_easy + 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nSQL:'
    return prompt



def GPT4_generation(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        n = 1,
        stream = False,
        temperature=0.0,
        max_tokens=600,
        top_p = 1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop = ["Q:"]
    )
    return response.choices[0].message.content



# Use the following to run after every function is correctly defined
# Remember to change the certain function names below into the ones that are created in previous steps
def process_question_sql(question, predicted_class, schema_links):
    if '"EASY"' in predicted_class:
        print("EASY")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(easy_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
    elif '"NON-NESTED"' in predicted_class:
        print("NON-NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(medium_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    else:
        print("NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(
                    hard_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    print(SQL)
    return SQL
    

############################################ SELF CORRECTION
def debuger(test_sample_text,sql):
	instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them and return the fixed SQLite QUERY in the output. If there are no issues, return the SQLite SQL QUERY as is in the output.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.
"""
	prompt = instruction + '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY'
	return prompt



def GPT4_debug(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        n = 1,
        stream = False,
        temperature=0.0,
        max_tokens=350,
        top_p = 1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop = ["#", ";","\n\n"]
    )
    return response.choices[0].message.content


def refine_query(question, sql):
	debugged_SQL = None
	while debugged_SQL is None:
		try:
			debugged_SQL = GPT4_debug(debuger(question,sql)).replace("\n", " ")
		except:
			time.sleep(3)
			pass
	SQL = debugged_SQL.split('sql', 1)
	print(SQL)

############################################


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
                },
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


@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/din-query")
async def process_din_query(query: Query):
    relevant_schema_links = ValueRetriever().process_question(query.question)
    predicted_class = process_question_classification(query.question,relevant_schema_links) 
    crude_sql = process_question_sql(query.question, predicted_class, relevant_schema_links)
    sql_query = refine_query()
    csv_results = execute_sql(sql_query)
    return {
        "sql_query": sql_query,
        "csv_results": csv_results  # CSV data embedded as a JSON field
    }




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
