classification_prompt = '''Q: "Find the filing date and submission number of all reports filed for an NPORT-P submission."
schema_links: [submission.filing_date, submission.sub_type = "NPORT-P", submission.accession_number]
A: Let’s think step by step. The SQL query for the question "Find the filing date and submission number of all reports filed for an NPORT-P submission." needs these tables = [submission], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""]. 
So, we don't need JOIN and don't need nested queries, then the SQL query can be classified as "EASY".
Label: "EASY"

Q: "Get the names and CIK of registrants who are located in California."
schema_links: [registrant.registrant_name, registrant.cik, registrant.state = "US-CA"]
A: Let’s think step by step. The SQL query for the question "Get the names and CIK of registrants who are located in California." needs these tables = [registrant], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""]. 
So, we don't need JOIN and don't need nested queries, then the SQL query can be classified as "EASY".
Label: "EASY"

Q: "Find the names and CIK of registrants in California, but only for those whose total assets are above 100 million."
schema_links: [registrant.registrant_name, registrant.cik, registrant.state = "US-CA", fund_reported_info.total_assets > 100000000]
A: Let's analyze this. The query involves data from two tables: "registrant" for registrant details and "fund_reported_info" for total assets. Since we need to check if total assets exceed 100 million, a nested query is necessary to filter based on this condition. This is a nested query. So, the SQL query can be classified as "NESTED."
Label: "NESTED"

'''


easy_prompt = '''Q: "Find the issuers with a balance greater than 1 million."
Schema_links: [fund_reported_holding.balance]
SQL: SELECT DISTINCT issuer_name 
      FROM fund_reported_holding 
      WHERE balance > 1000000
'''

medium_prompt = '''Q: "Find the total upfront payments and receipts for swaps with fixed rate receipts."
Schema_links: [nonforeign_exchange_swap.upfront_payment, nonforeign_exchange_swap.upfront_receipt, nonforeign_exchange_swap.fixed_rate_receipt]
A: Let’s think step by step. For creating the SQL for the given question, we need to filter the swaps that have fixed rate receipts. Then, sum up the upfront payments and receipts. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: 
SELECT SUM(nonforeign_exchange_swap.upfront_payment) + SUM(nonforeign_exchange_swap.upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE nonforeign_exchange_swap.fixed_rate_receipt IS NOT NULL
SQL: 
SELECT SUM(upfront_payment) + SUM(upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE fixed_rate_receipt IS NOT NULL
'''

hard_prompt = '''Q: "Find the borrowers with aggregate value greater than $1 million and whose interest rate change at 10-year maturity for a 100 basis point change is positive."
Schema_links: [borrower.aggregate_value, borrower.name, interest_rate_risk.intrst_rate_change_10yr_dv100]
A: Let's think step by step. First, we need to filter borrowers with aggregate values greater than $1 million. Then, we need to check for interest rate changes at 10-year maturity where the change is positive. 
The SQL query for the sub-question "What are the borrowers with aggregate value greater than $1 million and positive interest rate change at 10-year maturity for 100 basis points?" is:

Intermediate_representation: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0

SQL: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0
'''

def hard_prompt_maker(test_sample_text,database,schema_links,sub_questions):
  instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
#   fields = find_fields_MYSQL_like("college_2")
#   fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
  fields += "\n"
  prompt = instruction + fields + hard_prompt + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question"'
  return prompt

def medium_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
#   fields = find_fields_MYSQL_like("college_2")
#   fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction +fields + medium_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt

def easy_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
#   fields = find_fields_MYSQL_like("college_2")
  fields += find_fields_MYSQL_like(database)
  fields += "\n"
  prompt = instruction +fields + easy_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
  return prompt

def classification_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
  instruction += "\nif need nested queries: predict NESTED\n"
  instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
  instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
#   fields = find_fields_MYSQL_like("college_2")
#   fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction + fields + classification_prompt + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt