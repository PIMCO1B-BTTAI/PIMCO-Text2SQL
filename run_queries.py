import sqlite3
import re
import os
import csv
from typing import List, Tuple
import pandas as pd

def extract_queries(text: str) -> List[Tuple[str, str]]:
    pattern = r'(\d+)\.\s*"([^"]+)"[\s\n]*((WITH[\s\S]+?;|SELECT[\s\S]+?;))'
    
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
    parsed_queries = []
    
    for num, question, sql, _ in matches:
        clean_sql = sql.strip()
        if clean_sql:
            parsed_queries.append((question, clean_sql))
    
    print(f"Found {len(parsed_queries)} queries")
    return parsed_queries

def extract_all_query_sets(prompt_content: str) -> List[Tuple[str, str]]:
    all_queries = []
    
    sections = [
        ('easy', r'gpt_queries_easy\s*=\s*"""(.*?)"""'),
        ('medium', r'gpt_queries_medium\s*=\s*"""(.*?)"""'),
        ('hard', r'gpt_queries_hard\s*=\s*"""(.*?)"""')
    ]
    
    for difficulty, pattern in sections:
        matches = re.search(pattern, prompt_content, re.DOTALL)
        if matches:
            queries_text = matches.group(1)
            queries = extract_queries(queries_text)
            print(f"{len(queries)} {difficulty}")
            all_queries.extend(queries)
        else:
            print(f"Warning: Could not find {difficulty} query set in the prompt file")
    
    print(f"Total queries found: {len(all_queries)}")
    return all_queries

def run_all_queries_to_df(queries: List[Tuple[str, str]], db_path: str, output_file: str):
    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to database at {db_path}")
        
        results_data = []
        
        for question, sql in queries:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                
                results_data.append({
                    'Question': question,
                    'SQL': sql,
                    'Result_Count': len(rows),
                    'Status': 'Success'
                })
                
                print(f"Successfully executed query for: {question[:50]}...")
                
            except Exception as e:
                results_data.append({
                    'Question': question,
                    'SQL': sql,
                    'Result_Count': 0,
                    'Status': f'Failed: {str(e)}'
                })
                print(f"Error in query: {str(e)}")
        
        df = pd.DataFrame(results_data)
        df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
        print(f"\nAll results saved to {output_file}")
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

def main():
    db_path = os.path.join('sqlite', 'nport.db')
    prompt_path = os.path.join('chatgpt_api', 'chat_prompt_V3.py')
    output_file = os.path.join('chatgpt_api', 'query_summary.csv')
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
            
            all_queries = extract_all_query_sets(prompt_content)
            
            if all_queries:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                run_all_queries_to_df(all_queries, db_path, output_file)
            else:
                print("No queries found in the prompt file")
                
    except FileNotFoundError as e:
        print(f"File not found error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()