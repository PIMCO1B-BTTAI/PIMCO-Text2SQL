# Define the latest available time period for data querying
latest_time_period = "2024Y"

# Background and Table Structure
overall_task_instructions = """
Task:
The task is to convert the natural language query into a SQL query.
This involves parsing the intent of the query and understanding the structure of the data to generate an appropriate SQL command.
"""

# TO BE CHANGED based on our current database
# SQL Table being queried
table_name = 'Joined'
table_name_instructions = f"""
SQL Table:
The only table to be queried is the '{table_name}' table. This table is a join between the 'SUBMISSION' and 'REGISTRANT' tables,
which include details about EDGAR filings and registrant data, respectively.
"""

# TO BE CHANGED based on our current database
# Detailed overview of the table to guide the model
table_overview_instructions = f"""
Table Overview:
- The '{table_name}' table combines information from the 'SUBMISSION' and 'REGISTRANT' tables.
- It features unique filings identified by 'ACCESSION_NUMBER', linking submission-specific details with registrant identifiers.
- Fields include dates, submission types, registrant names, CIK numbers, addresses, and more.
- This table is critical for understanding the connection between filings and registrants across various reporting periods.
"""

# Schema information as plain text with descriptions for each column
schema_info = """
Database Schema:

Table: SUBMISSION
- This table contains information from the EDGAR(Electronic Data Gathering, Analysis, and Retrieval) submission
- ACCESSION_NUMBER (Primary Key): 
    This is a 20-character identifier that is unique to every document 
    submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
    The first 10 digits represent the entity making the filing, 
    followed by the filing year (24 for 2024), and the sequence of the filing.
    This unique number allows users and regulators to track this specific report.
- FILING_DATE: 
    This is the date when the report was officially submitted to the SEC, 
    meaning the fund handed in its NPORT report on this specific filling date.
- FILE_NUM: 
    File number associated with the filing which is used to uniquely track and 
    categorize the registration and regulatory documents of the investment 
    company with the SEC. Filings may not have a file number if they are not 
    directly associated with a specific fund registration.
- SUB_TYPE: 
    Type of submission 
    NPORT-P: standard monthly report
    NPORT-P/A: an amendment to correct or update a previously filed NPORT-P
    NT NPORT-P: a notification that the regular NPORT-P filing will be late, requesting more time to submit it.
- REPORT_ENDING_PERIOD: 
    This is the final date of the period covered by the report. 
    It is the date of fiscal year-end for the report, which marks the 
    end of the company's or fund's business year for financial reporting purposes.
- REPORT_DATE: 
    Specific date on which the financial and portfolio data provided in the report 
    are accurate and reflect the fund's holdings and performance. 
- IS_LAST_FILING: 
    This field indicates whether this is the fund's final report. 
    'N' means this is not the last report for the fund, and the fund will continue to submit future reports.

"""

# Instructions for handling parts of the natural language query
nlp_query_handling_instructions = """
Natural Language Processing Instructions:
- Decompose the user's query to identify requirements regarding asset classes, sectors, time periods, or specific filings.
- Detect keywords related to filing dates, submission types, registrant details, and financial data.
- Default to the most recent time period ('2024Y') if not specified, and consider all asset classes unless otherwise mentioned.
"""

# SQL Query Format template to guide the generated SQL command
sql_query_template_instructions = """
SQL Query Format:
- Use the following format to construct queries:
    SELECT [columns]
    FROM '{table_name}'
    WHERE [conditions]
- Replace '[columns]' with actual column names based on the query.
- Construct '[conditions]' based on specifics derived from the natural language query.
"""

# Define default behavior for unspecified fields or conditions
default_query_behavior = f"""
Default Behavior:
- Assume the most recent data period ('{latest_time_period}') if no time period is specified.
- Include all asset classes and sectors unless specified in the query.
- Retrieve all filings if no specific criteria are provided.
"""

# Example Natural Language Queries and Corresponding SQL Translations
example_queries = """
Examples:
1. "List the top 5 registrants by total net assets, including their CIK and country."
   SQL: 
   WITH FundAssets AS (
       SELECT R.CIK, R.REGISTRANT_NAME, R.COUNTRY, F.NET_ASSETS
       FROM REGISTRANT R
       JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   )
   SELECT CIK, REGISTRANT_NAME, COUNTRY, NET_ASSETS
   FROM FundAssets
   ORDER BY NET_ASSETS DESC
   LIMIT 5;

2. "Find all holdings with a fair value level of Level 1 and their corresponding fund names."
   SQL: 
   WITH HoldingsCTE AS (
       SELECT H.HOLDING_ID, H.ISSUER_NAME, H.FAIR_VALUE_LEVEL, F.SERIES_NAME
       FROM FUND_REPORTED_HOLDING H
       JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
       WHERE H.FAIR_VALUE_LEVEL = 'Level 1'
   )
   SELECT HOLDING_ID, ISSUER_NAME, SERIES_NAME
   FROM HoldingsCTE;

3. "Calculate the total collateral amount for repurchase agreements grouped by counterparty."
   SQL: 
   WITH CollateralCTE AS (
    SELECT RCP.NAME AS Counterparty_Name, SUM(RC.COLLATERAL_AMOUNT) AS Total_Collateral
    FROM REPURCHASE_COLLATERAL RC
    JOIN REPURCHASE_COUNTERPARTY RCP ON RC.HOLDING_ID = RCP.HOLDING_ID
    GROUP BY RCP.NAME
   )
   SELECT Counterparty_Name, Total_Collateral
   FROM CollateralCTE
   ORDER BY Total_Collateral DESC;

4. "Locate funds that have both securities lending activities and repurchase agreements."
   SQL: 
   WITH SecuritiesLending AS (
       SELECT ACCESSION_NUMBER
       FROM SECURITIES_LENDING
       WHERE IS_LOAN_BY_FUND = 'Y'
   ),
   RepurchaseAgreements AS (
       SELECT ACCESSION_NUMBER
       FROM REPURCHASE_AGREEMENT
   )
   SELECT F.SERIES_NAME
   FROM FUND_REPORTED_INFO F
   WHERE F.ACCESSION_NUMBER IN (SELECT ACCESSION_NUMBER FROM SecuritiesLending)
     AND F.ACCESSION_NUMBER IN (SELECT ACCESSION_NUMBER FROM RepurchaseAgreements);

5. "Find borrowers who have borrowed more than $5,000,000, including their names and LEIs."
   SQL: 
   WITH BorrowedAmounts AS (
       SELECT BORROWER_ID, SUM(AGGREGATE_VALUE) AS Total_Borrowed
       FROM BORROWER
       GROUP BY BORROWER_ID
       HAVING SUM(AGGREGATE_VALUE) > 5000000
   )
   SELECT B.NAME, B.LEI, BA.Total_Borrowed
   FROM BORROWER B
   JOIN BorrowedAmounts BA ON B.BORROWER_ID = BA.BORROWER_ID;

6. "List all derivative counterparties along with the number of derivative instruments they are involved in."
   SQL: 
   WITH CounterpartyCounts AS (
       SELECT DC.DERIVATIVE_COUNTERPARTY_NAME, COUNT(*) AS Instrument_Count
       FROM DERIVATIVE_COUNTERPARTY DC
       JOIN FUND_REPORTED_HOLDING H ON DC.HOLDING_ID = H.HOLDING_ID
       JOIN DEBT_SECURITY D ON H.HOLDING_ID = D.HOLDING_ID
       GROUP BY DC.DERIVATIVE_COUNTERPARTY_NAME
   )
   SELECT DERIVATIVE_COUNTERPARTY_NAME, Instrument_Count
   FROM CounterpartyCounts
   ORDER BY Instrument_Count DESC;

7. "Compute the average annualized rate for debt securities grouped by coupon type."
   SQL: 
   WITH RateAverages AS (
       SELECT DS.COUPON_TYPE, AVG(DS.ANNUALIZED_RATE) AS Avg_Annualized_Rate
       FROM DEBT_SECURITY DS
       WHERE DS.ANNUALIZED_RATE IS NOT NULL
       GROUP BY DS.COUPON_TYPE
   )
   SELECT COUPON_TYPE, Avg_Annualized_Rate
   FROM RateAverages
   ORDER BY Avg_Annualized_Rate DESC;

8. "Get funds that have experienced a net decrease in assets over the last three reporting periods."
   SQL: 
   WITH AssetChanges AS (
       SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, S.REPORT_DATE, F.NET_ASSETS,
              LAG(F.NET_ASSETS, 1) OVER (PARTITION BY F.SERIES_NAME ORDER BY S.REPORT_DATE) AS Previous_Period_Assets
       FROM FUND_REPORTED_INFO F
       JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
   )
   SELECT DISTINCT AC.SERIES_NAME
   FROM AssetChanges AC
   WHERE AC.NET_ASSETS < AC.Previous_Period_Assets
     AND AC.Previous_Period_Assets IS NOT NULL;

9. "Identify issuers with more than three different securities holdings, including their names and CUSIPs."
   SQL: 
   WITH IssuerHoldings AS (
       SELECT H.ISSUER_NAME, H.ISSUER_CUSIP, COUNT(DISTINCT H.HOLDING_ID) AS Holding_Count
       FROM FUND_REPORTED_HOLDING H
       GROUP BY H.ISSUER_NAME, H.ISSUER_CUSIP
       HAVING COUNT(DISTINCT H.HOLDING_ID) > 3
   )
   SELECT ISSUER_NAME, ISSUER_CUSIP, Holding_Count
   FROM IssuerHoldings
   ORDER BY Holding_Count DESC;

10. "Calculate the total notional amount of derivatives per currency and identify the top 3 currencies by notional amount."
    SQL: 
    WITH NotionalSums AS (
        SELECT ODNA.CURRENCY_CODE, SUM(ODNA.NOTIONAL_AMOUNT) AS Total_Notional
        FROM OTHER_DERIV_NOTIONAL_AMOUNT ODNA
        GROUP BY ODNA.CURRENCY_CODE
    )
    SELECT CURRENCY_CODE, Total_Notional
    FROM NotionalSums
    ORDER BY Total_Notional DESC
    LIMIT 3;

11. "List funds with liquidation preferences exceeding their net assets."
    SQL: 
    WITH FundPreferences AS (
        SELECT F.SERIES_NAME, F.LIQUIDATION_PREFERENCE, F.NET_ASSETS
        FROM FUND_REPORTED_INFO F
    )
    SELECT SERIES_NAME, LIQUIDATION_PREFERENCE, NET_ASSETS
    FROM FundPreferences
    WHERE LIQUIDATION_PREFERENCE > NET_ASSETS;

12. "Find all convertible securities that are contingent and have a conversion ratio above 1.5."
    SQL: 
    WITH ConvertibleCTE AS (
        SELECT DS.HOLDING_ID, CSC.CONVERSION_RATIO
        FROM DEBT_SECURITY DS
        JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON DS.HOLDING_ID = CSC.HOLDING_ID
        WHERE DS.IS_CONVTIBLE_CONTINGENT = 'Y' AND CSC.CONVERSION_RATIO > 1.5
    )
    SELECT HOLDING_ID, CONVERSION_RATIO
    FROM ConvertibleCTE;

13. "Retrieve the total unrealized appreciation for each asset category across all funds."
    SQL: 
    WITH AppreciationCTE AS (
        SELECT H.ASSET_CAT, SUM(H.PERCENTAGE * H.CURRENCY_VALUE) AS Total_Unrealized_App
        FROM FUND_REPORTED_HOLDING H
        GROUP BY H.ASSET_CAT
    )
    SELECT ASSET_CAT, Total_Unrealized_App
    FROM AppreciationCTE
    ORDER BY Total_Unrealized_App DESC;

14. "Analyze the distribution of asset categories within the top 10 largest funds by total assets."
    SQL: 
    WITH TopFunds AS (
        SELECT SERIES_NAME, ACCESSION_NUMBER
        FROM FUND_REPORTED_INFO
        ORDER BY TOTAL_ASSETS DESC
        LIMIT 10
    ),
    AssetDistribution AS (
        SELECT H.ASSET_CAT, COUNT(*) AS Category_Count
        FROM FUND_REPORTED_HOLDING H
        JOIN TopFunds T ON H.ACCESSION_NUMBER = T.ACCESSION_NUMBER
        GROUP BY H.ASSET_CAT
    )
    SELECT ASSET_CAT, Category_Count
    FROM AssetDistribution
    ORDER BY Category_Count DESC;
"""


example_queries_2 = """
Examples:
1. "Find the top 10 funds with the highest average monthly returns in the past quarter."
   SQL: 
   WITH AvgMonthlyReturn AS (
       SELECT ACCESSION_NUMBER, 
              (MONTHLY_TOTAL_RETURN1 + MONTHLY_TOTAL_RETURN2 + MONTHLY_TOTAL_RETURN3) / 3.0 AS Avg_Return
       FROM MONTHLY_TOTAL_RETURN
   )
   SELECT F.SERIES_NAME, A.ACCESSION_NUMBER, A.Avg_Return
   FROM AvgMonthlyReturn A
   JOIN FUND_REPORTED_INFO F ON A.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY A.Avg_Return DESC
   LIMIT 10;

2. "Compare the latest net asset values of the top 5 performing funds."
   SQL: 
   WITH TopPerformingFunds AS (
    SELECT 
        ACCESSION_NUMBER, 
        (MONTHLY_TOTAL_RETURN1 + MONTHLY_TOTAL_RETURN2 + MONTHLY_TOTAL_RETURN3) / 3.0 AS Avg_Return
    FROM 
        MONTHLY_TOTAL_RETURN
    ORDER BY 
        Avg_Return DESC
    LIMIT 5
   )
   SELECT 
      FR.SERIES_NAME, 
      FR.NET_ASSETS, 
      TP.Avg_Return
   FROM 
      TopPerformingFunds TP
   JOIN 
      FUND_REPORTED_INFO FR ON TP.ACCESSION_NUMBER = FR.ACCESSION_NUMBER;

3. "Calculate the overall average return across all funds for the most recent month."
   SQL: 
   WITH LatestReturns AS (
    SELECT 
        M.ACCESSION_NUMBER, 
        M.MONTHLY_TOTAL_RETURN1
    FROM 
        MONTHLY_TOTAL_RETURN M
    JOIN 
        SUBMISSION S ON M.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    WHERE 
        S.REPORT_DATE = (SELECT MAX(REPORT_DATE) FROM SUBMISSION)
   )
   SELECT 
      AVG(MONTHLY_TOTAL_RETURN1) AS Average_Return
   FROM 
      LatestReturns;

4. "Find the interest rate risk for each fund and identify those with the highest risk scores."
   SQL: 
   WITH InterestRiskScores AS (
    SELECT 
        IR.ACCESSION_NUMBER, 
        -- Calculating composite risk score by summing absolute values of DV01 and DV100 columns
        (ABS(CAST(IR.INTRST_RATE_CHANGE_3MON_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_1YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_5YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_3MON_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_1YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_5YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_10YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_30YR_DV100 AS FLOAT))
        ) AS Composite_Risk_Score
    FROM 
        INTEREST_RATE_RISK IR
   )
   SELECT 
      FR.SERIES_NAME, 
      FR.ACCESSION_NUMBER, 
      IRS.Composite_Risk_Score
   FROM 
      InterestRiskScores IRS
   JOIN 
      FUND_REPORTED_INFO FR ON IRS.ACCESSION_NUMBER = FR.ACCESSION_NUMBER
   ORDER BY 
      IRS.Composite_Risk_Score DESC
   LIMIT 5;

5. "Determine which funds have the highest Value at Risk (VaR) based on their variable information."
   SQL: 
   WITH FundVaR AS (
       SELECT ACCESSION_NUMBER, 
              (VAR1 + VAR2 + VAR3) AS Total_VaR
       FROM FUND_VAR_INFO
   )
   SELECT F.SERIES_NAME, FV.ACCESSION_NUMBER, FV.Total_VaR
   FROM FundVaR FV
   JOIN FUND_REPORTED_INFO F ON FV.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY FV.Total_VaR DESC
   LIMIT 5;

6. "Identify funds that are most sensitive to interest rate changes."
   SQL: 
   WITH SensitivityScores AS (
       SELECT ACCESSION_NUMBER, SENSITIVITY_VALUE
       FROM INTEREST_RATE_RISK
       WHERE SENSITIVITY_VALUE IS NOT NULL
   )
   SELECT F.SERIES_NAME, SS.SENSITIVITY_VALUE
   FROM SensitivityScores SS
   JOIN FUND_REPORTED_INFO F ON SS.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY SS.SENSITIVITY_VALUE DESC
   LIMIT 5;

7. "Retrieve funds that have experienced a net decrease in assets over the last three reporting periods."
   SQL: 
   WITH AssetChanges AS (
       SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, S.REPORT_DATE, F.NET_ASSETS,
              LAG(F.NET_ASSETS, 1) OVER (PARTITION BY F.SERIES_NAME ORDER BY S.REPORT_DATE) AS Previous_Period_Assets
       FROM FUND_REPORTED_INFO F
       JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
   )
   SELECT DISTINCT AC.SERIES_NAME
   FROM AssetChanges AC
   WHERE AC.NET_ASSETS < AC.Previous_Period_Assets
     AND AC.Previous_Period_Assets IS NOT NULL;

8. "Analyze the composition of fund portfolios by categorizing assets and their total values."
   SQL: 
   WITH PortfolioComposition AS (
    SELECT 
        ACCESSION_NUMBER, 
        ASSET_CAT, 
        SUM(CAST(CURRENCY_VALUE AS FLOAT)) AS Total_Value
    FROM 
        FUND_REPORTED_HOLDING
    GROUP BY 
        ACCESSION_NUMBER, 
        ASSET_CAT
)
SELECT 
    F.SERIES_NAME, 
    PC.ASSET_CAT, 
    PC.Total_Value
FROM 
    PortfolioComposition PC
JOIN 
    FUND_REPORTED_INFO F ON PC.ACCESSION_NUMBER = F.ACCESSION_NUMBER
ORDER BY 
    F.SERIES_NAME, 
    PC.Total_Value DESC;

9. "Identify the most common asset categories across all fund portfolios."
    SQL: 
    WITH AssetCounts AS (
        SELECT ASSET_CAT, COUNT(*) AS Count
        FROM FUND_REPORTED_HOLDING
        GROUP BY ASSET_CAT
    )
    SELECT ASSET_CAT, Count
    FROM AssetCounts
    ORDER BY Count DESC
    LIMIT 5;

10. "Determine the percentage allocation of each asset category within individual fund portfolios."
    SQL: 
    WITH TotalAssets AS (
    SELECT 
        ACCESSION_NUMBER, 
        SUM(CAST(CURRENCY_VALUE AS FLOAT)) AS Total_Value
    FROM 
        FUND_REPORTED_HOLDING
    GROUP BY 
        ACCESSION_NUMBER
),
CategoryAllocation AS (
    SELECT 
        FH.ACCESSION_NUMBER, 
        FH.ASSET_CAT, 
        SUM(CAST(FH.CURRENCY_VALUE AS FLOAT)) AS Category_Value
    FROM 
        FUND_REPORTED_HOLDING FH
    GROUP BY 
        FH.ACCESSION_NUMBER, 
        FH.ASSET_CAT
   )
   SELECT 
      F.SERIES_NAME, 
      CA.ASSET_CAT, 
      (CA.Category_Value * 100.0 / TA.Total_Value) AS Percentage_Allocation
   FROM 
      CategoryAllocation CA
   JOIN 
      TotalAssets TA ON CA.ACCESSION_NUMBER = TA.ACCESSION_NUMBER
   JOIN 
      FUND_REPORTED_INFO F ON CA.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY 
      F.SERIES_NAME, 
      Percentage_Allocation DESC;

11. "Identify funds with significant derivative exposures exceeding one million in unrealized appreciation."
    SQL: 
    WITH SignificantExposures AS (
        SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, SUM(D.UNREALIZED_APPRECIATION) AS Total_Derivative_Exposure
        FROM SWAPTION_OPTION_WARNT_DERIV D
        JOIN FUND_REPORTED_HOLDING FH ON D.HOLDING_ID = FH.HOLDING_ID
        JOIN FUND_REPORTED_INFO F ON FH.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        GROUP BY F.ACCESSION_NUMBER, F.SERIES_NAME
        HAVING SUM(D.UNREALIZED_APPRECIATION) > 1000000
    )
    SELECT SERIES_NAME, ACCESSION_NUMBER, Total_Derivative_Exposure
    FROM SignificantExposures
    ORDER BY Total_Derivative_Exposure DESC;
    """

# Reasoning instructions
reasoning_instruction = """
```
1. Reasoning you provide should first focus on why a nested query was chosen or why it wasn't chosen.
2. It should give a query plan on how to solve this question - explain 
the mapping of the columns to the words in the input question.
3. It should explain each of the clauses and why they are structured the way they are structured. 
   For example, if there is a `GROUP BY`, an explanation should be given as to why it exists.
4. If there's any `SUM()` or any other function used, it should be explained as to why it was required.
```

```
Format the generated SQL with proper indentation - the columns in the 
(`SELECT` statement should have more indentation than the keyword `SELECT` 
and so on for each SQL clause.)
```
"""

# Full prompt 
full_prompt = (
    overall_task_instructions +
    table_name_instructions +
    table_overview_instructions +
    nlp_query_handling_instructions +
    sql_query_template_instructions +
    default_query_behavior +
    example_queries +
    example_queries_2 +
    reasoning_instruction
)
# Output the full prompt
print(full_prompt)


import openai
import logging
from fastapi import HTTPException

# Set up the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Construct the function that takes in the user's question 
# and returning the SQL commands with reasoning in json format
def generate_sql_and_reasoning(user_question: str) -> dict:
    # Append the user question to the full prompt
    prompt_with_question = full_prompt + f"\n\nUser Question: {user_question}\n"

    try:
        # Call the OpenAI API to generate the SQL query and reasoning
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # Adjust model if needed
            prompt=prompt_with_question,
            max_tokens=300,  # Adjust token limit as per your need
            temperature=0.7
        )

        # Extract the reasoning and the SQL query from the response
        generated_text = response.choices[0].text.strip()

        # Assuming reasoning and SQL are separated by a newline in the response
        reasoning, sql_query = generated_text.split("\n", 1)

        return {
            "reasoning": reasoning.strip(),
            "SQL Query": sql_query.strip()
        }

    except openai.error.OpenAIError as e:
        logger.error(f"Error with OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")