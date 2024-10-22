# Define the latest available time period for data querying
latest_time_period = "2024Y"

# Background and Table Structure
overall_task_instructions = """
Task:
The task is to convert the natural language query into a SQL query.
This involves parsing the intent of the query and understanding the structure of the data to generate an appropriate SQL command.
"""

# SQL Table being queried
table_name = 'Joined'
table_name_instructions = f"""
SQL Table:
The only table to be queried is the '{table_name}' table. This table is a join between the 'SUBMISSION' and 'REGISTRANT' tables,
which include details about EDGAR filings and registrant data, respectively.
"""

# Detailed overview of the table to guide the model
table_overview_instructions = f"""
Table Overview:
- The '{table_name}' table combines information from the 'SUBMISSION' and 'REGISTRANT' tables.
- It features unique filings identified by 'ACCESSION_NUMBER', linking submission-specific details with registrant identifiers.
- Fields include dates, submission types, registrant names, CIK numbers, addresses, and more.
- This table is critical for understanding the connection between filings and registrants across various reporting periods.
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
1. "What are the recent filings by CIK number 0001234567?"
   SQL: SELECT * FROM {table_name} WHERE CIK='0001234567' AND REPORT_DATE='2024Y'

2. "Show all filings for registrants in California since 2023"
   SQL: SELECT * FROM {table_name} WHERE STATE='CA' AND REPORT_DATE >= '2023Y'

3. "List all EDGAR submissions that were the last filings"
   SQL: SELECT * FROM {table_name} WHERE IS_LAST_FILING='Y'

4. "Find the total number of filings by each registrant in 2024"
   SQL: SELECT REGISTRANT_NAME, COUNT(*) FROM {table_name} WHERE REPORT_DATE='2024Y' GROUP BY REGISTRANT_NAME
"""

# Full prompt combining all elements
full_prompt = (
    overall_task_instructions +
    table_name_instructions +
    table_overview_instructions +
    nlp_query_handling_instructions +
    sql_query_template_instructions +
    default_query_behavior +
    example_queries
)

# Output the full prompt
print(full_prompt)
