import pandas as pd
import time
import openai
import os
import sys
from dotenv import load_dotenv
load_dotenv()


def debuger(test_sample_text,database,sql):
  instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.

"""
  fields = find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "Primary_keys = " + find_primary_keys_MYSQL_like(database)
  prompt = instruction + fields+ '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY\nSELECT'
  return prompt

def GPT4_debug(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-4",
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
  return response['choices'][0]['message']['content']

if __name__ == '__main__':
    spider_schema,spider_primary,spider_foreign = creatiing_schema(DATASET_SCHEMA)
    val_df = load_data(DATASET)
    print(f"Number of data samples {val_df.shape[0]}")
    CODEX = []
    for index, row in val_df.iterrows():
        #if index < 405: continue #for testing
        print(f"index is {index}")
        print(row['query'])
        print(row['question'])
        
        debugged_SQL = None
        while debugged_SQL is None:
            try:
                debugged_SQL = GPT4_debug(debuger(row['question'], row['db_id'], SQL)).replace("\n", " ")
            except:
                time.sleep(3)
                pass
        SQL = "SELECT " + debugged_SQL
        print(SQL)