import os
import sys
import time
import json
import csv
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import sqlite3
import pandas as pd
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from rapidfuzz import fuzz
from dotenv import load_dotenv

# Download required NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Setup paths and environment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from chatgpt_api import chat_prompt_V3

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OpenAI API key not configured")

# Constants
SCHEMA_FILE = os.path.join(parent_dir, 'chatgpt_api/schema.json')
OUTPUT_DIR = os.path.join(parent_dir, 'test_outputs')
ACCURACY_FILE = os.path.join(parent_dir, 'din_accuracy_with_mapping.csv')
TEMP_QUERIES_FILE = os.path.join(parent_dir, 'temp_queries.json')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Column mapping definitions
EQUIVALENT_COLUMNS = {
    # Example format:
    # 'original_column': ['equivalent_column1', 'equivalent_column2']
    'HOLDING_ID': ['HOLDING_NUMBER', 'HOLDING_IDENTIFIER'],
    'ACCESSION_NUMBER': ['ACCESSION_ID', 'ACCESSION_IDENTIFIER'],
    'FUND_NAME': ['FUND_IDENTIFIER', 'FUND_ID'],
    # Add more equivalent columns as needed
}

def normalize_column_name(column: str) -> str:
    """Normalize column name for comparison."""
    return column.upper().strip()

def are_columns_equivalent(col1: str, col2: str) -> bool:
    """Check if two columns are equivalent based on the mapping."""
    col1_norm = normalize_column_name(col1)
    col2_norm = normalize_column_name(col2)
    
    if col1_norm == col2_norm:
        return True
        
    for original, equivalents in EQUIVALENT_COLUMNS.items():
        if col1_norm == original and col2_norm in equivalents:
            return True
        if col2_norm == original and col1_norm in equivalents:
            return True
    
    return False

def extract_columns_from_sql(sql_query: str) -> List[str]:
    """Extract column names from SQL query."""
    # Remove string literals to avoid false matches
    sql_no_strings = re.sub(r"'[^']*'", "", sql_query)
    sql_no_strings = re.sub(r'"[^"]*"', "", sql_no_strings)
    
    # Find all words that might be column names
    # This is a simplified approach - in practice you might need more sophisticated parsing
    potential_columns = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', sql_no_strings)
    
    # Filter out SQL keywords
    sql_keywords = {'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'JOIN', 'ON', 'AND', 'OR', 'IN', 'NOT', 'NULL', 'AS'}
    columns = [col for col in potential_columns if col.upper() not in sql_keywords]
    
    return columns

def compare_queries_with_mapping(generated_sql: str, ground_truth_sql: str) -> Tuple[bool, List[str], List[str]]:
    """Compare two SQL queries considering column mapping."""
    gen_columns = extract_columns_from_sql(generated_sql)
    truth_columns = extract_columns_from_sql(ground_truth_sql)
    
    # Check if all columns in ground truth have equivalent columns in generated SQL
    matched_columns = []
    unmatched_columns = []
    
    for truth_col in truth_columns:
        found_match = False
        for gen_col in gen_columns:
            if are_columns_equivalent(truth_col, gen_col):
                matched_columns.append((truth_col, gen_col))
                found_match = True
                break
        if not found_match:
            unmatched_columns.append(truth_col)
    
    # Consider queries equivalent if all important columns are matched
    queries_equivalent = len(unmatched_columns) == 0
    
    return queries_equivalent, matched_columns, unmatched_columns

def execute_sql_query(query: str, db_path: str) -> Optional[pd.DataFrame]:
    """Execute SQL query and return results as DataFrame."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error executing SQL query: {str(e)}")
        return None

def compare_query_results(generated_df: pd.DataFrame, ground_truth_df: pd.DataFrame, column_mapping: List[Tuple[str, str]]) -> bool:
    """Compare query results considering column mapping."""
    if generated_df is None or ground_truth_df is None:
        return False
        
    # Rename columns in generated DataFrame according to mapping
    rename_map = {gen_col: truth_col for truth_col, gen_col in column_mapping}
    generated_df = generated_df.rename(columns=rename_map)
    
    # Sort both DataFrames to ensure consistent comparison
    generated_df = generated_df.sort_values(by=list(generated_df.columns))
    ground_truth_df = ground_truth_df.sort_values(by=list(ground_truth_df.columns))
    
    # Reset indices after sorting
    generated_df = generated_df.reset_index(drop=True)
    ground_truth_df = ground_truth_df.reset_index(drop=True)
    
    # Compare the DataFrames
    return generated_df.equals(ground_truth_df)

def log_test_results(query_num: int, test_result: str, generated_sql: str, ground_truth_sql: str, 
                    matched_columns: List[Tuple[str, str]], unmatched_columns: List[str]) -> None:
    """Log test results to file."""
    output_file = os.path.join(OUTPUT_DIR, f'test_output_{query_num}.txt')
    
    with open(output_file, 'w') as f:
        f.write(f"Test #{query_num} Results\n")
        f.write("=" * 80 + "\n")
        f.write(f"Test Result: {test_result}\n\n")
        
        f.write("Generated SQL:\n")
        f.write(generated_sql + "\n\n")
        
        f.write("Ground Truth SQL:\n")
        f.write(ground_truth_sql + "\n\n")
        
        f.write("Column Mapping:\n")
        for truth_col, gen_col in matched_columns:
            f.write(f"  {truth_col} -> {gen_col}\n")
        
        if unmatched_columns:
            f.write("\nUnmatched Columns:\n")
            for col in unmatched_columns:
                f.write(f"  {col}\n")

def update_accuracy_csv(query_num: int, test_result: str, column_match_rate: float) -> None:
    """Update accuracy CSV file with test results."""
    row = {
        'query_number': query_num,
        'result': test_result,
        'column_match_rate': column_match_rate
    }
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(ACCURACY_FILE):
        with open(ACCURACY_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
    
    # Append result
    with open(ACCURACY_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)

def run_accuracy_test(query_num: int, generated_sql: str, ground_truth_sql: str, db_path: str) -> None:
    """Run accuracy test with column mapping for a single query."""
    # Compare queries considering column mapping
    queries_equivalent, matched_columns, unmatched_columns = compare_queries_with_mapping(
        generated_sql, ground_truth_sql
    )
    
    # Calculate column match rate
    total_columns = len(matched_columns) + len(unmatched_columns)
    column_match_rate = len(matched_columns) / total_columns if total_columns > 0 else 0.0
    
    # Execute queries and compare results if queries are equivalent
    if queries_equivalent:
        generated_df = execute_sql_query(generated_sql, db_path)
        ground_truth_df = execute_sql_query(ground_truth_sql, db_path)
        
        results_match = compare_query_results(generated_df, ground_truth_df, matched_columns)
        test_result = "True" if results_match else "False"
    else:
        test_result = "False"
    
    # Log results
    log_test_results(query_num, test_result, generated_sql, ground_truth_sql, 
                    matched_columns, unmatched_columns)
    
    # Update accuracy CSV
    update_accuracy_csv(query_num, test_result, column_match_rate)

def analyze_results() -> None:
    """Analyze and print test results summary."""
    if not os.path.exists(ACCURACY_FILE):
        print("No test results found.")
        return
        
    df = pd.read_csv(ACCURACY_FILE)
    
    # Calculate statistics
    total_tests = len(df)
    true_results = len(df[df['result'] == 'True'])
    false_results = len(df[df['result'] == 'False'])
    avg_column_match_rate = df['column_match_rate'].mean()
    
    print("\nTest Results Summary")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {true_results} ({true_results/total_tests*100:.2f}%)")
    print(f"Failed Tests: {false_results} ({false_results/total_tests*100:.2f}%)")
    print(f"Average Column Match Rate: {avg_column_match_rate*100:.2f}%")

def main():
    """Main function to run the accuracy tests."""
    # Your main testing loop would go here
    # This would typically involve:
    # 1. Loading test cases
    # 2. Running the Text2SQL model
    # 3. Running accuracy tests
    # 4. Analyzing results
    pass

if __name__ == "__main__":
    main() 