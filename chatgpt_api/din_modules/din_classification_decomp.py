from openai import OpenAI
from dotenv import load_dotenv
import os
import time
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
		raise ValueError("OpenAI API key not configured")


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

def classification_prompt_maker(question,relevant_schema_links):
  instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
  instruction += "\nif need nested queries: predict NESTED\n"
  instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
  instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
  prompt = instruction + classification_prompt + 'Q: "' + question + '\nrelevant_schema_links: ' + relevant_schema_links + '\nA: Let’s think step by step.'
  return prompt

def process_question(question,relevant_schema_links):
	classification = None
	while classification is None:
			try:
					classification = client.chat.completions.create(
						model="gpt-4o",
						messages=[{"role": "user", "content": classification_prompt_maker(question, relevant_schema_links=relevant_schema_links)}],
						n = 1,
						stream = False,
						temperature=0.0,
						max_tokens=600,
						top_p = 1.0,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						stop = ["Q:"]
					).choices[0].message.content
			except:
					time.sleep(3)
					pass
	try:
			predicted_class = classification.split("Label: ")[1]
	except:
			print("Slicing error for the classification module")
			predicted_class = '"NESTED"'
	return predicted_class