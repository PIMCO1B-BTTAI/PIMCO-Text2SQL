import pandas as pd
import openai
import time
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def GPT4_generation(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-4",
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
  return response['choices'][0]['message']['content']

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

# Use the following to run after every function is correctly defined
# Remember to change the certain function names below into the ones that are created in previous steps
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
        schema_links = None
        while schema_links is None:
            try:
                schema_links = GPT4_generation(
                    schema_linking_prompt_maker(row['question'], row['db_id']))
            except:
                time.sleep(3)
                pass
        try:
            schema_links = schema_links.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        #print(schema_links)
        classification = None
        while classification is None:
            try:
                classification = GPT4_generation(
                    classification_prompt_maker(row['question'], row['db_id'], schema_links[1:]))
            except:
                time.sleep(3)
                pass
        try:
            predicted_class = classification.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'
        #print(classification)
        if '"EASY"' in predicted_class:
            print("EASY")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(easy_prompt_maker(row['question'], row['db_id'], schema_links))
                except:
                    time.sleep(3)
                    pass
        elif '"NON-NESTED"' in predicted_class:
            print("NON-NESTED")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(medium_prompt_maker(row['question'], row['db_id'], schema_links))
                except:
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                SQL = "SELECT"
        else:
            sub_questions = classification.split('questions = ["')[1].split('"]')[0]
            print("NESTED")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(
                        hard_prompt_maker(row['question'], row['db_id'], schema_links, sub_questions))
                except:
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                SQL = "SELECT"
        print(SQL)
        debugged_SQL = None
        while debugged_SQL is None:
            try:
                debugged_SQL = GPT4_debug(debuger(row['question'], row['db_id'], SQL)).replace("\n", " ")
            except:
                time.sleep(3)
                pass
        SQL = "SELECT " + debugged_SQL
        print(SQL)
        CODEX.append([row['question'], SQL, row['query'], row['db_id']])
        #break
    df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
    results = df['PREDICTED SQL'].tolist()
    with open(OUTPUT_FILE, 'w') as f:
        for line in results:
            f.write(f"{line}\n")