from openai import OpenAI
import json
import sqlite3
import csv
import io
import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from typing import Optional
from . import chat_prompt

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if not client.api_key:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not configured")

logger.info("OpenAI API key loaded successfully")

app = FastAPI()

class Query(BaseModel):
    question: str

def load_schema_from_json(file_path: str) -> dict:
    logger.debug(f"Attempting to load schema from {file_path}")
    try:
        with open(file_path, 'r') as f:
            schema = json.load(f)
        logger.info("Schema loaded successfully")
        return schema
    except FileNotFoundError:
        logger.error(f"Schema file not found at {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Schema file not found at {file_path}"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error decoding JSON schema: {str(e)}"
        )


def format_schema_for_gpt(schema: dict) -> str:
    try:
        formatted_schema = ""
        for table in schema.get('tables', []):
            table_name = table['url'].replace('.tsv', '')
            columns = table['tableSchema']['columns']
            column_list = ", ".join([
                f"{col['name']} {col['datatype']['base'].upper()}"
                for col in columns
            ])
            formatted_schema += f"{table_name}: {column_list}\n"
        return formatted_schema
    except Exception as e:
        logger.error(f"Error formatting schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error formatting schema: {str(e)}"
        )


# Path to the JSON schema file
SCHEMA_FILE = 'chatgpt_api/schema.json'
print(f"Expected schema path: {SCHEMA_FILE}")  # Add this line to see the path in logs

try:
    db_schema = load_schema_from_json(SCHEMA_FILE)
except Exception as e:
    logger.error(f"Failed to load initial schema: {str(e)}")
    db_schema = None

schema_info = format_schema_for_gpt(db_schema) 


def get_prompt() -> str:
    try:
        from . import chat_prompt
        return chat_prompt.full_prompt
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to load chat prompt: {str(e)}")
        return ""

from typing import List, Tuple, Dict
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from rapidfuzz.distance.Levenshtein import distance
from rapidfuzz import fuzz
import re
############################################ VALUE RETRIEVAL

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

class PSLsh:
    def __init__(self, vectors, n_planes=10, n_tables=5, seed: int = 42):
        self.n_planes = n_planes
        self.n_tables = n_tables
        self.hash_tables = [{} for _ in range(n_tables)]
        self.random_planes = []
        
        np.random.seed(seed)
        
        for _ in range(n_tables):
            planes = np.random.randn(vectors.shape[1], n_planes)
            self.random_planes.append(planes)
            
        self.num_vectors = vectors.shape[0]
        self.vectors = vectors
        self.build_hash_tables()

    def build_hash_tables(self):
        for idx in range(self.num_vectors):
            vector = self.vectors[idx].toarray()[0]
            hashes = self.hash_vector(vector)
            for i, h in enumerate(hashes):
                if h not in self.hash_tables[i]:
                    self.hash_tables[i][h] = []
                self.hash_tables[i][h].append(idx)

    def hash_vector(self, vector):
        hashes = []
        for planes in self.random_planes:
            projections = np.dot(vector, planes)
            hash_code = ''.join(['1' if x > 0 else '0' for x in projections])
            hashes.append(hash_code)
        return hashes

    def query(self, vector):
        hashes = self.hash_vector(vector)
        candidates = set()
        for i, h in enumerate(hashes):
            candidates.update(self.hash_tables[i].get(h, []))
        return candidates


class ValueRetrieval:
    financial_terms = {
            'total': ['total', 'sum', 'aggregate', 'combined'],
            'assets': ['asset', 'holdings', 'investments', 'securities'],
            'liabilities': ['liability', 'debt', 'obligations'],
            'net': ['net', 'pure', 'adjusted'],
            'fund': ['fund', 'portfolio', 'investment vehicle'],
            'return': ['return', 'yield', 'profit', 'gain'],
            'monthly': ['monthly', 'month', 'monthly basis'],
            'rate': ['rate', 'percentage', 'ratio'],
            'risk': ['risk', 'exposure', 'vulnerability']
        }
    def __init__(self, schema_path: str = 'chatgpt_api/schema.json', lsh_seed: int = 42):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Load schema
        print("DEBUG: Loading schema file:", schema_path)
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

        # Initialize lemmatizer and stop words
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Build column name index
        self.column_index = self._build_column_index()
        
        # Build common financial terms dictionary
        

        # Build vectorizer and LSH for backup matching
        self.build_vectorizer_and_lsh(seed=lsh_seed)
        
        # Get schema relationships
        self.primary_keys, self.foreign_keys = self.discover_schema_relationships()

    def _build_column_index(self) -> Dict:
        """Build an index of all columns with their metadata."""
        column_index = {}
        tables = self.schema.get('schema', {}).get('tables', [])
        
        for table in tables:
            table_name = table.get('name', '').lower()
            for column in table.get('columns', []):
                column_name = column.get('name', '').lower()
                
                # Store both the full qualified name and column properties
                qualified_name = f"{table_name}.{column_name}"
                column_index[qualified_name] = {
                    'table': table_name,
                    'column': column_name,
                    'type': column.get('type', ''),
                    'words': self._split_column_name(column_name),
                    'synonyms': self._get_column_synonyms(column_name)
                }
                
        return column_index

    def _split_column_name(self, column_name: str) -> List[str]:
        """Split column name into individual words."""
        # Handle both underscore and camel case
        words = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', column_name)).split()
        words.extend(column_name.split('_'))
        return [word.lower() for word in words if word]

    def _get_column_synonyms(self, column_name: str) -> List[str]:
        """Get synonyms for words in column name."""
        words = self._split_column_name(column_name)
        synonyms = []
        
        for word in words:
            if word in self.financial_terms:
                synonyms.extend(self.financial_terms[word])
                
        return list(set(synonyms))

    def build_vectorizer_and_lsh(self, seed: int):
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3), min_df=1, max_df=0.95)
        self.term_list = self.get_schema_terms()
        self.term_vectors = self.vectorizer.fit_transform(self.term_list)
        self.lsh = PSLsh(self.term_vectors, n_planes=10, n_tables=5)

    def get_schema_terms(self) -> List[str]:
        terms = []
        tables = self.schema.get('schema', {}).get('tables', [])
        for table in tables:
            table_name = table.get('name', '').lower()
            terms.append(table_name)
            for column in table.get('columns', []):
                column_name = column.get('name', '').lower()
                terms.append(f"{table_name}.{column_name}")
        return terms

    def discover_schema_relationships(self):
        # Define our primary keys and foreign keys here
        primary_keys = {
            'SUBMISSION': ['ACCESSION_NUMBER'],
            'REGISTRANT': ['ACCESSION_NUMBER'],
            'FUND_REPORTED_INFO': ['ACCESSION_NUMBER'],
            'INTEREST_RATE_RISK': ['ACCESSION_NUMBER', 'INTEREST_RATE_RISK_ID'],
            'BORROWER': ['ACCESSION_NUMBER', 'BORROWER_ID'],
            'BORROW_AGGREGATE': ['ACCESSION_NUMBER', 'BORROW_AGGREGATE_ID'],
            'MONTHLY_TOTAL_RETURN': ['ACCESSION_NUMBER', 'MONTHLY_TOTAL_RETURN_ID'],
            'MONTHLY_RETURN_CAT_INSTRUMENT': ['ACCESSION_NUMBER', 'ASSET_CAT', 'INSTRUMENT_KIND'],
            'FUND_VAR_INFO': ['ACCESSION_NUMBER'],
            'FUND_REPORTED_HOLDING': ['ACCESSION_NUMBER', 'HOLDING_ID'],
            'IDENTIFIERS': ['HOLDING_ID', 'IDENTIFIERS_ID'],
            'DEBT_SECURITY': [],  
            'DEBT_SECURITY_REF_INSTRUMENT': ['HOLDING_ID', 'DEBT_SECURITY_REF_ID'],
            'CONVERTIBLE_SECURITY_CURRENCY': ['HOLDING_ID', 'CONVERTIBLE_SECURITY_ID'],
            'REPURCHASE_AGREEMENT': ['HOLDING_ID'],
            'REPURCHASE_COUNTERPARTY': ['HOLDING_ID', 'REPURCHASE_COUNTERPARTY_ID'],
            'REPURCHASE_COLLATERAL': ['HOLDING_ID', 'REPURCHASE_COLLATERAL_ID'],
            'DERIVATIVE_COUNTERPARTY': ['HOLDING_ID', 'DERIVATIVE_COUNTERPARTY_ID'],
            'SWAPTION_OPTION_WARNT_DERIV': ['HOLDING_ID'],
            'DESC_REF_INDEX_BASKET': ['HOLDING_ID'],
            'DESC_REF_INDEX_COMPONENT': ['HOLDING_ID', 'DESC_REF_INDEX_COMPONENT_ID'],
            'DESC_REF_OTHER': ['HOLDING_ID', 'DESC_REF_OTHER_ID'],
            'FUT_FWD_NONFOREIGNCUR_CONTRACT': ['HOLDING_ID'],
            'FWD_FOREIGNCUR_CONTRACT_SWAP': ['HOLDING_ID'],
            'NONFOREIGN_EXCHANGE_SWAP': ['HOLDING_ID'],
            'FLOATING_RATE_RESET_TENOR': ['HOLDING_ID', 'RATE_RESET_TENOR_ID'],
            'OTHER_DERIV': ['HOLDING_ID'],
            'OTHER_DERIV_NOTIONAL_AMOUNT': ['HOLDING_ID', 'OTHER_DERIV_NOTIONAL_AMOUNT_ID'],
            'SECURITIES_LENDING': ['HOLDING_ID'],
            'EXPLANATORY_NOTE': ['ACCESSION_NUMBER', 'EXPLANATORY_NOTE_ID']
        }

        foreign_keys = [
            # ACCESSION_NUMBER relationships
            'REGISTRANT.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'INTEREST_RATE_RISK.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'BORROWER.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'BORROW_AGGREGATE.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'MONTHLY_TOTAL_RETURN.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'MONTHLY_RETURN_CAT_INSTRUMENT.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'FUND_VAR_INFO.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'FUND_REPORTED_HOLDING.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'EXPLANATORY_NOTE.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',
            'SUBMISSION.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER',

            # HOLDING_ID relationships
            'IDENTIFIERS.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DEBT_SECURITY.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DEBT_SECURITY_REF_INSTRUMENT.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'CONVERTIBLE_SECURITY_CURRENCY.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'REPURCHASE_AGREEMENT.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'REPURCHASE_COUNTERPARTY.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'REPURCHASE_COLLATERAL.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DERIVATIVE_COUNTERPARTY.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'SWAPTION_OPTION_WARNT_DERIV.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DESC_REF_INDEX_BASKET.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DESC_REF_INDEX_COMPONENT.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'DESC_REF_OTHER.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'FUT_FWD_NONFOREIGNCUR_CONTRACT.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'FWD_FOREIGNCUR_CONTRACT_SWAP.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'NONFOREIGN_EXCHANGE_SWAP.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'FLOATING_RATE_RESET_TENOR.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'OTHER_DERIV.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'OTHER_DERIV_NOTIONAL_AMOUNT.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID',
            'SECURITIES_LENDING.HOLDING_ID = FUND_REPORTED_HOLDING.HOLDING_ID'
        ]

        formatted_pks = []
        for table, keys in primary_keys.items():
            for key in keys:
                formatted_pks.append(f"{table}.{key}")

        return formatted_pks, foreign_keys

    def find_similar_words(self, word: str) -> List[Tuple[str, float]]:
        """Enhanced matching using multiple techniques."""
        if not word:
            return []

        word = word.lower()
        print(f"\nDEBUG: Finding matches for '{word}'")
        
        matches = []
        
        # 1. Direct matching with column names and their components
        for qualified_name, metadata in self.column_index.items():
            score = 0.0
            
            # Check exact matches in column words
            if word in metadata['words']:
                matches.append((qualified_name, 1.0))
                continue
                
            # Check synonyms
            if word in self.financial_terms.get(word, []):
                matches.append((qualified_name, 0.9))
                continue
            
            # Fuzzy match with column words
            for col_word in metadata['words']:
                ratio = fuzz.ratio(word, col_word) / 100.0
                if ratio > score:
                    score = ratio
            
            # Fuzzy match with synonyms
            for term, synonyms in self.financial_terms.items():
                if term in metadata['words']:
                    for synonym in synonyms:
                        ratio = fuzz.ratio(word, synonym) / 100.0
                        if ratio > score:
                            score = ratio * 0.9  # Slightly lower weight for synonym matches
            
            if score > 0.6:  # Only include if similarity is above 60%
                matches.append((qualified_name, score))

        # 2. LSH-based matching as backup
        if len(matches) < 5:  # If we have fewer than 5 matches, try LSH
            try:
                word_vector = self.vectorizer.transform([word]).toarray()[0]
                candidate_indices = self.lsh.query(word_vector)
                
                for idx in candidate_indices:
                    term = self.term_list[idx]
                    if not any(term == m[0] for m in matches):  # Avoid duplicates
                        candidate_vector = self.term_vectors[idx].toarray()[0]
                        dist = np.linalg.norm(word_vector - candidate_vector)
                        sim = 1 / (1 + dist)
                        if sim > 0.5:  # Only include if similarity is above 50%
                            matches.append((term, sim * 0.8))
            except Exception as e:
                print(f"LSH matching failed: {e}")

        # Remove duplicates keeping highest score and sort by score
        unique_matches = {}
        for term, score in matches:
            if term not in unique_matches or score > unique_matches[term]:
                unique_matches[term] = score
        
        matches = [(term, score) for term, score in unique_matches.items()]
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Print debug info
        print(f"Found {len(matches)} matches for '{word}':")
        for match, score in matches[:5]:
            print(f"  {match}: {score:.4f}")
        
        return matches[:5] if matches else [('fund_reported_info.total_assets', 0.6)] if word in ['total', 'asset', 'assets'] else []

    def extract_keywords(self, question: str) -> Dict:
        system_prompt = """You are an expert financial data analyst specializing in natural language understanding and database schema analysis.
Your task is to analyze questions about financial data and extract key components that will help in database queries.

Objective: Break down the given question into essential components that will help formulate a database query.

Instructions:
1. Read the question carefully to identify:
- Individual keywords that map to database columns or values
- Technical terms related to financial data
- Named entities (companies, funds, locations)
- Numerical thresholds or values

2. For each identified element, categorize it as:
- keywords: Individual significant words that might match database columns
- keyphrases: Multi-word expressions that represent single concepts
- named_entities: Specific names of companies, funds, or locations
- numerical_values: Any numbers, amounts, or thresholds

3. Return a JSON object with these categories."""

        few_shot_examples = """
Example Question: "Which PIMCO funds were registered between 2020 and 2023 with California addresses?"
{
    "keywords": ["funds", "registered", "addresses"],
    "keyphrases": ["PIMCO funds"],
    "named_entities": ["PIMCO", "California"],
    "numerical_values": ["2020", "2023"]
}

Example Question: "Show me BlackRock funds with total assets over 1 billion managed in New York"
{
    "keywords": ["funds", "assets", "managed"],
    "keyphrases": ["total assets"],
    "named_entities": ["BlackRock", "New York"],
    "numerical_values": ["1 billion"]
}"""

        formatted_prompt = system_prompt
        user_prompt = f"Question: \"{question}\"\n\nExtract the key components and return as JSON."

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": few_shot_examples + "\n" + user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def preprocess_text(self, text: str) -> List[str]:
        tokens = nltk.word_tokenize(text.lower())
        filtered_tokens = [word for word in tokens if word not in self.stop_words and word.isalnum()]
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in filtered_tokens]
        return lemmatized_tokens
    
    def process_question(self, question: str) -> Dict:
        # Extract keywords using gpt
        extracted_info = self.extract_keywords(question)

        words = []
        for key in ['keywords', 'keyphrases', 'named_entities', 'numerical_values']:
            words.extend(extracted_info.get(key, []))

        # Preprocess the words (lemmatize, remove stop words)
        processed_words = []
        for word in words:
            processed_words.extend(self.preprocess_text(word))

        # Remove duplicates
        processed_words = list(set(processed_words))

        # Find similar columns for each word
        similar_matches = {}
        for word in processed_words:
            similar_matches[word] = self.find_similar_words(word)

        # Combine the results
        result = {
            "question": question,
            "extracted_info": extracted_info,
            "processed_words": processed_words,
            "similar_matches": similar_matches,
            "schema_relationships": {
                "primary_keys": self.primary_keys,
                "foreign_keys": self.foreign_keys
            }
        }
        return result
    
############################################ CLASSIFICATION

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

def process_question_classification(question,relevant_schema_links):
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
############################################ SQL GENERATION
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

def hard_prompt_maker(question,database,schema_links,sub_questions=""):
    instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
    if sub_questions=="":
        stepping = f'''\nA: Let's think step by step. "{question}" can be solved by first solving a sub-question using nested queries".'''
    else:
        stepping = f'''\nA: Let's think step by step. "{question}" can be solved by first solving the answer to the following sub-question "{sub_questions}".'''
    prompt = instruction + hard_prompt+ chat_prompt.gpt_queries_hard+ 'Q: "' + question + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question:"'
    return prompt

def medium_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
    prompt = instruction + medium_prompt + chat_prompt.gpt_queries_medium+ 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
    return prompt

def easy_prompt_maker(question,database,schema_links):
    instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
    prompt = instruction + easy_prompt + chat_prompt.gpt_queries_easy + 'Q: "' + question + '\nSchema_links: ' + schema_links + '\nSQL:'
    return prompt



def GPT4_generation(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        n = 1,
        stream = False,
        temperature=0.0,
        max_tokens=600,
        top_p = 1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop = ["Q:"]
    )
    return response.choices[0].message.content



# Use the following to run after every function is correctly defined
# Remember to change the certain function names below into the ones that are created in previous steps
def process_question_sql(question, predicted_class, schema_links):
    if '"EASY"' in predicted_class:
        print("EASY")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(easy_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
    elif '"NON-NESTED"' in predicted_class:
        print("NON-NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(medium_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    else:
        print("NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = GPT4_generation(
                    hard_prompt_maker(question, schema_links))
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    print(SQL)
    return SQL
    

############################################ SELF CORRECTION
def debuger(test_sample_text,sql):
	instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them and return the fixed SQLite QUERY in the output. If there are no issues, return the SQLite SQL QUERY as is in the output.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.
"""
	prompt = instruction + '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY'
	return prompt



def GPT4_debug(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        n = 1,
        stream = False,
        temperature=0.0,
        max_tokens=350,
        top_p = 1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop = ["#", ";","\n\n"]
    )
    return response.choices[0].message.content


def refine_query(question, sql):
	debugged_SQL = None
	while debugged_SQL is None:
		try:
			debugged_SQL = GPT4_debug(debuger(question,sql)).replace("\n", " ")
		except:
			time.sleep(3)
			pass
	SQL = debugged_SQL.split('sql', 1)
	print(SQL)

############################################


# LLM prompting for SQL generation
def generate_sql(question: str) -> str:
    logger.debug(f"Generating SQL for question: {question}")
    
    if not db_schema:
        logger.error("Database schema not loaded")
        raise HTTPException(
            status_code=500,
            detail="Database schema not loaded"
        )

    #schema_info = format_schema_for_gpt(db_schema) 
    prompt = f"""
    ```
    OVERALL TASK:
    I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question: {question}
    ```
    """ + get_prompt()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial database assistant that generates SQL queries based on natural language questions about financial data."
                },
                {"role": "user", "content": prompt}
            ],
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "sql_query",
                        "description": "Execute SQL queries against the database schema which includes tables like FUND_REPORTED_INFO (containing SERIES_NAME, TOTAL_ASSETS) and REGISTRANT (containing REGISTRANT_NAME). Use these tables to analyze fund data.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The SQL query to execute. Example: To find top PIMCO funds, use: SELECT SERIES_NAME, TOTAL_ASSETS FROM FUND_REPORTED_INFO JOIN REGISTRANT ON FUND_REPORTED_INFO.ACCESSION_NUMBER = REGISTRANT.ACCESSION_NUMBER WHERE REGISTRANT_NAME LIKE '%PIMCO%' ORDER BY TOTAL_ASSETS DESC LIMIT 5"
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    "schema": schema_info # this is where the schema is entered
                }
            ], 
        tool_choice={"type": "function", "function": {"name": "sql_query"}}  # force the model to use the SQL function
        )

        function_call = response.choices[0].message.tool_calls[0].function
        if function_call.name == "sql_query":
            # openai returns function arguments as a JSON string, so we need to parse it
            # The query will be in the "query" field of the parsed JSON
            sql_query = json.loads(function_call.arguments)["query"]
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
        else:
            raise ValueError(f"Unexpected function call: {function_call.name}")

    except Exception as e:
        logger.error(f"Unexpected error generating SQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL: {str(e)}"
    )

def execute_sql(query: str) -> str:
    logger.debug(f"Executing SQL query: {query}")
    conn = None
    try:
        conn = sqlite3.connect('sqlite/nport.db')
        cursor = conn.cursor()

        # Execute the query with a timeout
        cursor.execute(query)

        # Fetch column names and rows
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Convert the results to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        csv_data = output.getvalue()
        output.close()

        logger.info("SQL query executed successfully")
        return csv_data
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error executing SQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing SQL: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


def get_column_mapping(db_sql: str, gpt_sql: str) -> dict:
    """
    Uses GPT to generate a mapping between two SQL queries' columns
    
    db_sql (str): The SQL query that actually runs on the database
    gpt_sql (str): The SQL query generated by GPT
    
    Returns mapping of database columns to GPT columns
    """

    prompt = f"""Given these two SQL queries, create a JSON mapping of column names from Query 1 to Query 2:

    Query 1 (Database): {db_sql}
    Query 2 (Generated): {gpt_sql}
    
    Return only a JSON mapping where keys are column names from Query 1 and values are corresponding column names from Query 2.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a SQL expert that creates column mappings between queries."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        mapping = json.loads(response.choices[0].message.content)
        logger.info(f"Generated column mapping: {mapping}")
        return mapping
        
    except Exception as e:
        logger.error(f"Error generating column mapping: {str(e)}")
        return {}


@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.post("/din-query")
async def process_din_query(query: Query):
    relevant_schema_links = ValueRetriever().process_question(query.question)
    predicted_class = process_question_classification(query.question,relevant_schema_links) 
    crude_sql = process_question_sql(query.question, predicted_class, relevant_schema_links)
    sql_query = refine_query(crude_sql)
    csv_results = execute_sql(sql_query)
    return {
        "sql_query": sql_query,
        "csv_results": csv_results  # CSV data embedded as a JSON field
    }




@app.post("/query")
async def process_query(query: Query):
    logger.info(f"Processing query: {query.question}")
    try:
        sql_query = generate_sql(query.question)
        logger.info(f"Processing query: {query.question}")
        csv_results = execute_sql(sql_query)
        return {
            "sql_query": sql_query,
            "csv_results": csv_results  # CSV data embedded as a JSON field
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/schema-raw")
async def get_raw_schema():
    return db_schema

@app.get("/schema")
async def get_schema():
    if not db_schema:
        raise HTTPException(
            status_code=500,
            detail="Schema not loaded"
        )
    return {"schema": format_schema_for_gpt(db_schema)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
