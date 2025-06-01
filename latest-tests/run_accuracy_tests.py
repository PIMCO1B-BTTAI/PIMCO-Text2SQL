import os
import json
import pandas as pd
from accuracy_with_column_mapping import run_accuracy_test, analyze_results

def load_test_cases(test_file: str) -> list:
    """Load test cases from CSV file."""
    df = pd.read_csv(test_file)
    return df.to_dict('records')

def main():
    # Configure paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    test_cases_file = os.path.join(parent_dir, 'query_summary.csv')
    db_path = os.path.join(parent_dir, 'sqlite/din.db')

    # Load test cases
    print("Loading test cases...")
    test_cases = load_test_cases(test_cases_file)
    total_cases = len(test_cases)
    print(f"Loaded {total_cases} test cases")

    # Run tests
    print("\nRunning accuracy tests with column mapping...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nProcessing test case {i}/{total_cases}")
        
        # Extract query information
        query_num = test_case['query_number']
        generated_sql = test_case['generated_sql']
        ground_truth_sql = test_case['ground_truth_sql']
        
        # Run accuracy test
        try:
            run_accuracy_test(
                query_num=query_num,
                generated_sql=generated_sql,
                ground_truth_sql=ground_truth_sql,
                db_path=db_path
            )
            print(f"✓ Test case {i} completed")
        except Exception as e:
            print(f"✗ Error processing test case {i}: {str(e)}")

    # Analyze and print results
    print("\nAnalyzing results...")
    analyze_results()

if __name__ == "__main__":
    main() 