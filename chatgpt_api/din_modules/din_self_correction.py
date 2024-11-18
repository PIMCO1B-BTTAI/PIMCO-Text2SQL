import pandas as pd
import time
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
		raise ValueError("OpenAI API key not configured")



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