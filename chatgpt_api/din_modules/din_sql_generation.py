import pandas as pd
import openai
import time
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
		raise ValueError("OpenAI API key not configured")


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
    prompt = instruction + hard_prompt + 'Q: "' + question + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question"'
    return prompt

def medium_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
    prompt = instruction + medium_prompt + 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
    return prompt

def easy_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
    prompt = instruction + easy_prompt + 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nSQL:'
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
def process_question(question, predicted_class, schema_links):
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
    