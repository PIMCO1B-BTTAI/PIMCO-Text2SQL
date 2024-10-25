import pandas as pd
import logging
import io
from fastapi import FastAPI, HTTPException
from api import execute_sql


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    def compare_csv(ground_truth_query: str, llm_query: str) -> str:
        try: 
            logger.info("Executing grouth truth query...")
            ground_truth_csv = execute_sql(ground_truth_query)

            logger.info("Executing LLM query")
            llm_csv = execute_sql(llm_query)

            # Convert both CSV to pandas df to compare
            df_ground_truth = pd.read_csv(io.StringIO(ground_truth_csv))
            df_llm = pd.read_csv(io.StringIO(llm_csv))

            # compare df
            comparison = df_ground_truth.compare(df_llm)

            if comparison.empty:
                return {"result": "CSV outputs match perfectly."}
            else:
                return {"result": "Mismatch found.", "details": comparison.to_dict()}
        
        except Exception as e:
            logger.error(f"Error comparing CSVs: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error comparing CSVs: {str(e)}"
            )

if __name__ == "__main__":
    main()