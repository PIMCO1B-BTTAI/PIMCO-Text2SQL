import pandas as pd
import logging
import io
import requests
from fastapi import FastAPI, HTTPException
import chatgpt_api.api as api
import sys
import csv


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compare_csv(ground_truth_query: str, llm_query: str):
    ## let LLM stack query the database
    try: 
        logger.info("Executing LLM query")
        response = requests.post(
            "http://localhost:8000/query",
            json={"question": llm_query}
        )
        response.raise_for_status()
        result = response.json()
        generated_sql = result.get('sql_query', 'No SQL query generated.')

        llm_csv = result.get('csv_results','')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    
    
    ## direct query to the database
    logger.info("Executing grouth truth query...")
    ground_truth_csv = api.execute_sql(ground_truth_query)

    


    ## compare results
    
    try:
        diff=compare_csv_strings(ground_truth_csv,llm_csv)
            # compare df
        #df_ground_truth = pd.read_csv(io.StringIO(ground_truth_csv))
        #df_llm = pd.read_csv(io.StringIO(llm_csv))
        #diff = df_ground_truth.equals(df_llm)

        if diff:
            #return {"result": "CSV outputs match perfectly."}
            print("CSV outputs match perfectly.")
            return True
        else:
            #total_cells = df_llm.size
            #diff_cells = diff.count().sum()
            #difference_percentage = (diff_cells / total_cells) * 100
            #print(f"Mismatch found. Difference percentage: {difference_percentage:.2f}%")
            print("Mismatch found.")
            return False
    except Exception as e:
        logger.error(f"Error comparing CSVs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing CSVs: {str(e)}"
        )



def compare_csv_strings(csv_data1: str, csv_data2: str) -> bool:
    # Use io.StringIO to read the CSV strings as file-like objects
    csv_file1 = io.StringIO(csv_data1)
    csv_file2 = io.StringIO(csv_data2)
    
    # Create CSV readers for each CSV string
    reader1 = csv.reader(csv_file1)
    reader2 = csv.reader(csv_file2)
    
    # Compare rows one by one
    for row1, row2 in zip(reader1, reader2):
        if row1 != row2:
            return False  # Rows are different
    
    # Check if there are extra rows in either file
    try:
        next(reader1)
        return False  # Extra rows in csv_data1
    except StopIteration:
        pass

    try:
        next(reader2)
        return False  # Extra rows in csv_data2
    except StopIteration:
        pass

    return True  # CSVs are identical


def main():
    if len(sys.argv) == 3:
        # Access the arguments and run compare_csv
        ground_truth_query = sys.argv[1]
        llm_query = sys.argv[2]
        
        # Call the compare_csv function with the arguments
        compare_csv(ground_truth_query, llm_query)
    else:
        print("Error: Exactly two arguments are required.")
        print("Usage: python script_name.py <ground_truth_query> <llm_query>")


if __name__ == "__main__":
    main()

    