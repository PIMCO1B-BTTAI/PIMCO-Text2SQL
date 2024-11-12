import sqlite3
import csv
import re
import os
from typing import List, Tuple

def extract_queries(text: str) -> List[Tuple[str, str, str]]:
    """Extract numbered queries, questions and their SQL from the text."""
    pattern = r'(\d+)\. "([^"]+)"\n(SELECT[\s\S]+?;)'
    matches = re.findall(pattern, text)
    return [(num, question, sql.strip()) for num, question, sql in matches]

def run_all_queries_to_csv(queries: List[Tuple[str, str, str]], db_path: str, output_file: str):
    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to database at {db_path}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for num, question, sql in queries:
                writer.writerow([])
                writer.writerow([f"Query {num}"])
                writer.writerow([f"Question: {question}"])
                writer.writerow([f"SQL: {sql}"])
                writer.writerow([]) 
                
                try:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    
                    columns = [description[0] for description in cursor.description]
                    writer.writerow(columns)

                    rows = cursor.fetchall()
                    writer.writerows(rows)

                    writer.writerow([])
                    writer.writerow([f"Number of results: {len(rows)}"])
                    writer.writerow(["----------------------------------------"])
                    
                    print(f"Successfully executed query {num}")
                    
                except Exception as e:
                    writer.writerow([f"Error executing query: {str(e)}"])
                    print(f"Error in query {num}: {str(e)}")
        
        print(f"\nAll results saved to {output_file}")
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

def main():
    db_path = os.path.join('sqlite', 'nport.db')
    prompt_path = os.path.join('chatgpt_api', 'chat_prompt.py')
    output_file = os.path.join('chatgpt_api', 'all_query_results.csv')
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
            matches = re.search(r'gpt_queries_easy\s*=\s*"""(.*?)"""', prompt_content, re.DOTALL)
            if matches:
                queries_text = matches.group(1)
                queries = extract_queries(queries_text)
                
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                run_all_queries_to_csv(queries, db_path, output_file)
            else:
                print("Could not find gpt_queries_easy in the prompt file")
    
    except FileNotFoundError as e:
        print(f"File not found error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()