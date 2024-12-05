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
from . import chat_prompt, chat_prompt_revised
from chatgpt_api import chat_prompt_V3



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

naive_schema_info = format_schema_for_gpt(db_schema) 


def get_prompt() -> str:
    try:
        return chat_prompt.full_prompt
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to load chat prompt: {str(e)}")
        return ""


############################################ HERE BEGINS DIN-CHASE HYBRID

import sys
import os
import re
import time
import openai as OpenAI
from typing import List, Tuple, Dict
import json
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from rapidfuzz import fuzz
from . import chat_prompt_revised
print(os.getcwd())

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


# current_dir = os.path.dirname(os.path.abspath("/d/GithubRepos/PIMCO-Text2SQL"))
# din_modules_path = os.path.join(current_dir, 'chatgpt_api')
# sys.path.append(din_modules_path)

output_file = os.path.join(os.getcwd(), 'api_backend_logs.txt')
def append_to_file(output, filename=output_file):
    # Check if file exists
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write("Test_Din API Backend Log\n")
            file.write("=" * 80 + "\n")
    # Append the output
    with open(filename, 'a') as file:
        file.write(output + "\n" + "=" * 80 + "\n")

schema_info = chat_prompt_revised.schema_info

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

def GPT4_generation(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "user", "content": prompt}],
                n = 1,
                stream = False,
                temperature=0.0,
                #max_tokens=600,
                top_p = 1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
                # Removed stop=["Q:"] as it cause issues
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print("Max retries reached")
                return None
    return None

############################################ VALUE RETRIEVAL AND SCHEMA LINKING
############################################ VALUE RETRIEVAL AND SCHEMA LINKING
def schema_linking_prompt_maker(question):
  instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
  fields = format_schema_for_gpt(db_schema)
  foreign_keys = "Foreign_keys = " + foreign_keys + '\n'
  prompt = instruction + chat_prompt_V3.schema_linking_prompt + fields +foreign_keys+ 'Q: "' + question + """"\nA: Let’s think step by step."""
  return prompt

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

import re
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
        self.schema = db_schema

        # Initialize lemmatizer and stop words
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Build column name index
        self.column_index = self._build_column_index()        

        # Build vectorizer and LSH for backup matching
        self.build_vectorizer_and_lsh(seed=lsh_seed)
        
        # Get schema relationships
        self.primary_keys, self.foreign_keys = self.discover_schema_relationships()

    def _build_column_index(self) -> Dict:
        column_index = {}
        tables = self.schema.get('schema', {}).get('tables', [])
        
        for table in tables:
            table_name = table.get('name', '').lower()
            for column in table.get('columns', []):
                column_name = column.get('name', '').lower()
                
                # Store the full qualified name and column properties
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
        # Handle  underscore + camel case.
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
        #"""Better matching using multiple techniques - backup method with financial terms dictionary."""
        if not word:
            return []

        word = word.lower()
        #print(f"\nDEBUG: Finding matches for '{word}'")
        
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
        #print(f"Found {len(matches)} matches for '{word}':")
        #for match, score in matches[:5]:
            #print(f"  {match}: {score:.4f}")
        
        return matches[:5] if matches else [('fund_reported_info.total_assets', 0.6)] if word in ['total', 'asset', 'assets'] else []
    
    def extract_keywords(self, question: str) -> Dict:
        system_prompt = """Given a financial database schema: {schema_info}

        Primary Keys: {primary_keys}

        Foreign Keys: {foreign_keys}

        Extract from the question schema-aware components using the examples below."""

        few_shot_examples = """
        ```
        Example Question: "Show me all equity-focused funds"
        {
        "keywords": ["equity", "funds", "series"],
        "keyphrases": ["equity-focused funds"], 
        "table_matches": ["FUND_REPORTED_INFO"],
        "column_matches": ["SERIES_NAME", "TOTAL_ASSETS"],
        "primary_keys": ["FUND_REPORTED_INFO.ACCESSION_NUMBER"]
        }

        Example Question: "Show fund holdings over 1 billion in assets"
        {
        "keywords": ["holdings", "assets", "funds"],
        "numerical_values": ["1 billion"],
        "table_matches": ["FUND_REPORTED_INFO", "FUND_REPORTED_HOLDING"],
        "column_matches": ["TOTAL_ASSETS", "SERIES_NAME", "HOLDING_VALUE"],
        "required_joins": [
            "FUND_REPORTED_INFO to FUND_REPORTED_HOLDING via ACCESSION_NUMBER"
        ],
        "primary_keys": [
            "FUND_REPORTED_INFO.ACCESSION_NUMBER",
            "FUND_REPORTED_HOLDING.HOLDING_ID"
        ],
        "foreign_keys": [
            "FUND_REPORTED_HOLDING.ACCESSION_NUMBER = FUND_REPORTED_INFO.ACCESSION_NUMBER"
        ]
        }
        ```
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt.format(
                    schema_info=self.schema,
                    primary_keys=self.primary_keys,
                    foreign_keys=self.foreign_keys
                )},
                {"role": "user", "content": few_shot_examples + f"```\nQuestion: {question}\n```"}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "extract_components",
                    "description": "Extract components mapping to schema",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keywords": {"type": "array", "items": {"type": "string"}},
                            "keyphrases": {"type": "array", "items": {"type": "string"}},
                            "table_matches": {"type": "array", "items": {"type": "string"}},
                            "column_matches": {"type": "array", "items": {"type": "string"}},
                            "required_joins": {"type": "array", "items": {"type": "string"}},
                            "primary_keys": {"type": "array", "items": {"type": "string"}},
                            "foreign_keys": {"type": "array", "items": {"type": "string"}},
                            "numerical_values": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["keywords", "table_matches", "column_matches"]
                    }
                }
            }],
            tool_choice={"type": "function", "function": {"name": "extract_components"}}
        )

        function_call = response.choices[0].message.tool_calls[0].function
        return json.loads(function_call.arguments)

    def preprocess_text(self, text: str) -> List[str]:
        """Tokenize and lemmatize input text, removing stop words."""
        if not text:  # Add check for empty text
            return []
            
        try:
            tokens = nltk.word_tokenize(str(text).lower())
            filtered_tokens = [word for word in tokens if word not in self.stop_words and word.isalnum()]
            lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in filtered_tokens]
            return lemmatized_tokens
        except Exception as e:
            #print(f"Error in preprocessing text '{text}': {str(e)}")
            return []  # Return empty list instead of None on error
       
       
    def process_schema(self, question: str) -> str:
        # Get all the processing results
        results = self.process_question(question)
        
        # Organize schema links by type
        table_columns = []
        relevant_primary_keys = []
        relevant_foreign_keys = []
        
        # 1. Get main table/column matches
        for word, matches in results['similar_matches'].items():
            if matches:
                # Only take the top match if score > 0.7
                top_match = matches[0]  # (match, score)
                if top_match[1] > 0.7:
                    # Handle numerical values
                    if word in results['extracted_info'].get('numerical_values', []):
                        if 'billion' in word.lower():
                            table_columns.append(f"{top_match[0]} > 1000000000")
                        elif 'million' in word.lower():
                            table_columns.append(f"{top_match[0]} > 1000000")
                        else:
                            table_columns.append(f"{top_match[0]} > {word}")
                    else:
                        table_columns.append(top_match[0])
        
        # 2. Get relevant tables
        tables_needed = set()
        for link in table_columns:
            if '.' in link:
                tables_needed.add(link.split('.')[0].upper())
        
        # 3. Add relevant primary keys
        for pk in results['schema_relationships']['primary_keys']:
            table = pk.split('.')[0]
            if table in tables_needed:
                relevant_primary_keys.append(pk)
        
        # 4. Add relevant foreign keys
        for fk in results['schema_relationships']['foreign_keys']:
            tables_in_fk = set(part.split('.')[0] for part in fk.split(' = '))
            if tables_in_fk.intersection(tables_needed):
                relevant_foreign_keys.append(fk)
        #print("Attempting to generate schema_links")
        counterIndex = 0
        schema_links = None
        while schema_links is None and counterIndex<3:
            try:
                schema_links = GPT4_generation(schema_linking_prompt_maker(question))
            except:
                #print("Error while generating schema_link")
                counterIndex+=1
        try:
            schema_links = schema_links.split("Schema_links: ")[1]
        except:
            #print("Slicing error for the schema_linking module")
            schema_links = "[]"

        # Format output with sections
        schema_dict = {
            "table_columns": table_columns,
            "primary_keys": relevant_primary_keys,
            "foreign_keys": relevant_foreign_keys,
            "schema_links": schema_links
        }
        
        #print("\nProcessed Schema Links:")
        #print("Table Columns:", table_columns)
        #print("Primary Keys:", relevant_primary_keys)
        #print("Foreign Keys:", relevant_foreign_keys)
        
        return schema_dict


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
    
global_vr = ValueRetrieval(schema_path='chatgpt_api/schema.json')

############################################ CLASSIFICATION
############################################ CLASSIFICATION
classification_prompt = '''
```
Q: "Find the filing date and submission number of all reports filed for an NPORT-P submission."
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
```
'''

def classification_prompt_maker(question, schema_dict):
   instruction = """```
TASK OVERVIEW

Given the database schema:
{schema_info}

Relevant Columns:
{table_columns}

Relevant Primary Keys:
{primary_keys}

Relevant Foreign Keys:
{foreign_keys}

Schema Links:
{schema_links}

- For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN
- if need nested queries: predict NESTED
- elif need JOIN and don't need nested queries: predict NON-NESTED
- elif don't need JOIN and don't need nested queries: predict EASY

Consider table relationships and what joins would be needed.
```
"""

   prompt = instruction.format(
       schema_info=schema_info,
       table_columns=schema_dict["table_columns"],
       primary_keys=schema_dict["primary_keys"],
       foreign_keys=schema_dict["foreign_keys"],
       schema_links=schema_dict["schema_links"]
   ) + classification_prompt + f'Q: "{question}"\nschema_links: {schema_dict["schema_links"]}\nA: Let\'s think step by step.'
       
   return prompt

def process_question_classification(question, schema_dict):
    def extract_classification(text):
        #print(f"Trying to extract classification from: {text}")
        # Common patterns in GPT's response
        patterns = [
            "Label:", 
            "Classification:", 
            "The SQL query can be classified as",
            "can be classified as"
        ]
        
        text = text.upper()  # Normalize text
        # Direct class detection
        for class_type in ["EASY", "NON-NESTED", "NESTED"]:
            if class_type in text:
                return class_type

        # Try splitting with different patterns
        for pattern in patterns:
            if pattern.upper() in text:
                parts = text.split(pattern.upper())
                if len(parts) > 1:
                    # Get the last part and clean it
                    result = parts[1].strip().strip('"').strip("'")
                    # Extract first word as classification
                    classification = result.split()[0].strip()
                    if classification in ["EASY", "NON-NESTED", "NESTED"]:
                        return classification
                        
        return "NESTED"  # Default fallback

    classification = None
    attempts = 0
    while classification is None and attempts < 3:
        try:
            #print("Attempting classification...")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user", 
                    "content": classification_prompt_maker(question, schema_dict) #### ADD SCHEMA LINKS
                }],
                n=1,
                stream=False,
                temperature=0.0,
                #max_tokens=300,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            raw_response = response.choices[0].message.content
            #print("Raw response:", raw_response)
            classification = extract_classification(raw_response)
        except Exception as e:
            #print(f"Error occurred: {str(e)}")
            time.sleep(3)
            attempts += 1
            if attempts == 3:
                raise e
    
    final_class = classification if classification else "NESTED"
    return f'"{final_class}"', raw_response

############################################ SQL GENERATION
easy_example = '''
```
Example with reasoning process:

Q: "Find the issuers with a balance greater than 1 million."

schema_links: [fund_reported_holding.balance]

SQL: SELECT DISTINCT issuer_name 
      FROM fund_reported_holding 
      WHERE balance > 1000000;
```
'''

medium_example = '''
```
Example with reasoning process:

Q: "Find the total upfront payments and receipts for swaps with fixed rate receipts."

schema_links: [nonforeign_exchange_swap.upfront_payment, nonforeign_exchange_swap.upfront_receipt, nonforeign_exchange_swap.fixed_rate_receipt]

A: Let’s think step by step. For creating the SQL for the given question, we need to filter the swaps that have fixed rate receipts. Then, sum up the upfront payments and receipts. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: 
SELECT SUM(nonforeign_exchange_swap.upfront_payment) + SUM(nonforeign_exchange_swap.upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE nonforeign_exchange_swap.fixed_rate_receipt IS NOT NULL;

SQL: 
SELECT SUM(upfront_payment) + SUM(upfront_receipt) 
FROM nonforeign_exchange_swap 
WHERE fixed_rate_receipt IS NOT NULL;
```
'''

hard_example = '''
```
Example with reasoning process:

Q: "Find the borrowers with aggregate value greater than $1 million and whose interest rate change at 10-year maturity for a 100 basis point change is positive."

schema_links: [borrower.aggregate_value, borrower.name, interest_rate_risk.intrst_rate_change_10yr_dv100]

A: Let's think step by step. First, we need to filter borrowers with aggregate values greater than $1 million. Then, we need to check for interest rate changes at 10-year maturity where the change is positive. 
The SQL query for the sub-question "What are the borrowers with aggregate value greater than $1 million and positive interest rate change at 10-year maturity for 100 basis points?" is:

Intermediate_representation: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0;

SQL: 
SELECT borrower.name 
FROM borrower 
JOIN interest_rate_risk 
ON borrower.accession_number = interest_rate_risk.accession_number 
WHERE borrower.aggregate_value > 1000000 
AND interest_rate_risk.intrst_rate_change_10yr_dv100 > 0;
```
'''

def hard_prompt_maker(question, schema_dict, sub_questions=""):
   instruction = f"""```
OVERALL TASK:
I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question: {question}
You might need join statements and nested queries for this.
```
"""+"""```
Relevant Columns:
{table_columns}

Relevant Primary Keys:
{primary_keys}

Relevant Foreign Keys:
{foreign_keys}

Schema Links:
{schema_links}
```
""".format(
       table_columns=schema_dict["table_columns"],
       primary_keys=schema_dict["primary_keys"],
       foreign_keys=schema_dict["foreign_keys"],
       schema_links=schema_dict["schema_links"]
   )+chat_prompt_V3.common_part_prompt
   
   #if sub_questions=="":
       #stepping = "A: Let's think step by step." # {question} can be solved by first solving a sub-question using nested queries.
   #else:
       #stepping = "A: Let's think step by step."# {question} can be solved by first solving the answer to the following sub-question {sub_questions}.

   prompt = f"""{instruction}{hard_example}
```
Q: "{question}"

schema_links: {schema_dict["schema_links"]}
```

A: Let's think step by step."""
   return prompt

def medium_prompt_maker(question, schema_dict):
   instruction = f"""```
OVERALL TASK:
I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question: {question}
You should not need any nested queries, but you might need join statements for this question.
```
"""+"""```
Relevant Columns:
{table_columns}

Relevant Primary Keys:
{primary_keys}

Relevant Foreign Keys:
{foreign_keys}

Schema Links:
{schema_links}
```
""".format(
       table_columns=schema_dict["table_columns"],
       primary_keys=schema_dict["primary_keys"],
       foreign_keys=schema_dict["foreign_keys"],
       schema_links=schema_dict["schema_links"]
   )+chat_prompt_V3.common_part_prompt

   prompt = f"""{instruction}{medium_example}
```
Q: "{question}"

schema_links: {schema_dict["schema_links"]}
```

A: Let's think step by step."""
   return prompt

def easy_prompt_maker(question, schema_dict):
   instruction = f"""```
OVERALL TASK:
I will provide a database schema, generate an SQL query that retrieves from the database the answer to this question: {question}
You should not need any nested queries or join statements for this.
```
"""+"""```
Relevant Columns:
{table_columns}

Relevant Primary Keys:
{primary_keys}

Relevant Foreign Keys:
{foreign_keys}

Schema Links:
{schema_links}
```
""".format(
       table_columns=schema_dict["table_columns"],
       primary_keys=schema_dict["primary_keys"],
       foreign_keys=schema_dict["foreign_keys"],
       schema_links=schema_dict["schema_links"]
   )+chat_prompt_V3.common_part_prompt

   prompt = f"""{instruction}{easy_example} 
```
Q: "{question}"

schema_links: {schema_dict["schema_links"]}
```

SQL: """ #### ADD SCHEMA LINKS
   return prompt

from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any

thought_instructions = f"""
```
Thought Instructions:
```

```
Generate thoughts of increasing complexity.
Each thought should build on the previous ones and thoughts 
should progressively cover the nuances of the problem at hand.
```

```
First set of thoughts should be on whether a the query requires 
Common Table Expressions (CTEs) to calculate the
results for sub queries. 

Prefer using Common Table Expressions rather than
case when statements or nested subqueries.

If CTEs are required then for each CTE, an analysis of the purpose of each
CTE should be done.
An overall structure should be outlined as to what will be calculated in 
each CTE.
```

```
Next set of thoughts should on 
extracting out the names of as many of 
the relevant columns as possible for all CTEs and for all the sql clauses such as the 
`select`, `where` and `group_by` clauses.
There might be additions or deletions from this list based on the 
following additional thoughts to be generated.
```


```
Generate a thought to figure out the possible phrases in the query 
which can be used as values of the columns present in the table so as to use them 
in the `where` clause.
```

```
Generate a thought to compare these extracted values with the list of possible values
of columns listed in the information for the columns so as to use the exact string
in the `where` clause.
```

```
Generate a thought to reason whether `IS_TOP_TIER_ENTITY` flag is required or not.
```

```
Generate a thought to figure out which time period is being queried.
If nothing is specified use `PERIOD_ID = 2023Y`.
```

```
Generate a thought to figure out if a group_by clause is required.
```

```
The above thoughts about 
1. phrases for values of columns
2. query phrase to column value mapping
3. filters such as `ASSET_CAT` and others in the where clause
4. Period_id value to use
5. Group by column

should be generated for each of the CTE separately.
```

```
If the input question is similar to any of the examples given above,
then a thought should be generated to detect that and then that example 
should be followed closely to get the SQL for the input question given.
```

```
Closing Thoughts and Observations
```
These should summarize:
1. The structure of the SQL query:
    - This states whether the query has any nested query.
    If so, the structure of the nested query is also mentioned.
    If not, a summary of the function of each of the select`, `where`, `group_by` etc. clauses
    should be mentioned.
2. An explanation of how the query solves the user question.
"""

reasoning_instructions = """
```
1. Reasoning you provide should first focus on why a nested query was chosen or why it wasn't chosen.
2. It should give a query plan on how to solve this question - explain 
the mapping of the columns to the words in the input question.
3. It should explain each of the clauses and why they are structured the way they are structured. 
For example, if there is a `group_by`, an explanation should be given as to why it exists.
4. If there's any sum() or any other function used it should be explained as to why it was required.
```

```
Format the generated sql with proper indentation - the columns in the
(`select` statement should have more indentation than keyword `select`
and so on for each SQL clause.)
```
"""

# Final Output Schema
final_output_schema_json = json.dumps({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "user_nlp_query": {
            "type": "string",
            "description": "The original natural language query to be translated into SQL"
        },
        "reasonings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A thought about the user's question"
                    },
                    "helpful": {
                        "type": "boolean",
                        "description": "Whether the thought is helpful to solving the user's question"
                    }
                }
            },
            "description": "Step-by-step reasoning process for query generation"
        },
        "generated_sql_query": {
            "type": "string",
            "description": "The final SQL query that answers the natural language question"
        }
    }
})

class Thought(BaseModel):
    """A thought about the user's question"""
    thought: str = Field(
        description="Text of the thought"
    )
    helpful: bool = Field(
        description="Whether the thought is helpful to solving the user's question"
    )

class FinalOutput(BaseModel):
    """Complete output structure containing the query, reasoning, and SQL"""
    user_nlp_query: str = Field(
        description="The original natural language query to be translated into SQL"
    )
    reasonings: List[Thought] = Field(
        description="Step-by-step reasoning process for query generation"
    )
    generated_sql_query: str = Field(
        description="The final SQL query that answers the natural language question"
    )

def make_prompt(question: str, schema_dict: Dict[str, Any], complexity: str) -> str:
    """
    Create prompt with appropriate instructions based on complexity
    """
    example_output = {
        "user_nlp_query": question,
        "reasonings": [
            {
                "thought": "First, we need to identify the main tables required",
                "helpful": True
            },
            {
                "thought": "Next, determine if any joins or aggregations are needed",
                "helpful": True
            },
            {
                "thought": "Finally, consider how to structure the WHERE clause",
                "helpful": True
            }
        ],
        "generated_sql_query": "SELECT column FROM table WHERE condition;"
    }

    base_prompt = f"""
You are an expert SQL developer with deep knowledge of database querying.
Your task is to generate a SQL query with clear reasoning steps.

QUESTION: {question}

SCHEMA INFORMATION:
{schema_dict}

THOUGHT INSTRUCTIONS
{thought_instructions}

REASONING INSTRUCTIONS
{reasoning_instructions}

REQUIRED OUTPUT FORMAT:
The response must be a valid JSON object exactly matching this schema:
{final_output_schema_json}

Example of properly formatted response:
{json.dumps(example_output, indent=2)}

REASONING REQUIREMENTS:
1. Provide 3-5 thoughts explaining your strategy
2. Each thought should explain WHY you're taking an approach
3. Focus on query planning, not implementation details
4. Consider table relationships and data types

QUERY COMPLEXITY LEVEL: {complexity}
"""

    if complexity == "EASY":
        base_prompt += "\nRESTRICTIONS: No JOINs or nested queries allowed."
    elif complexity == "NON-NESTED":
        base_prompt += "\nRESTRICTIONS: JOINs allowed but no nested queries."
    else:
        base_prompt += "\nRESTRICTIONS: Both JOINs and nested queries allowed if needed."
        
    base_prompt += "\n\nIMPORTANT: Return only valid JSON with no additional text."
    
    return base_prompt

def generate_gpt_response(prompt, max_retries=3):
    """
    Generate response from OpenAI API with retries
    """
    system_prompt = """You are an expert SQL developer. Always return responses as valid JSON matching the specified schema. Include detailed reasoning steps before generating SQL queries."""
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                n=1,
                stream=False,
                temperature=0.0,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            #print(f"Raw GPT response:\n{content}")  
            return content
        except Exception as e:
            #print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                #print("Max retries reached")
                return None
    return None

def validate_gpt_response(response: str) -> bool:
    """
    Validate that GPT response contains all required fields
    """
    try:
        data = json.loads(response)
        required_fields = ["user_nlp_query", "reasonings", "generated_sql_query"]
        
        # Check all required fields exist in the output
        if not all(field in data for field in required_fields):
            #print("Missing required fields in response")
            return False
            
        if not isinstance(data["reasonings"], list) or len(data["reasonings"]) < 1:
            #print("Invalid reasonings array")
            return False
            
        # Check that each reasoning has required fields
        for reason in data["reasonings"]:
            if not all(field in reason for field in ["thought", "helpful"]):
                #print("Invalid reasoning format")
                return False
                
        return True
    except Exception as e:
        #print(f"Validation error: {str(e)}")
        return False

def process_question_sql(
    question: str,
    predicted_class: str,
    schema_dict: Dict[str, Any],
    max_retries: int = 3
) -> FinalOutput:
    """Generate SQL with thoughts and reasoning"""
    
    for attempt in range(max_retries):
        try:
            # Create appropriate prompt depending on classification module
            prompt = make_prompt(
                question=question,
                schema_dict=schema_dict,
                complexity=predicted_class
            )
            
            # Get GPT response
            response = generate_gpt_response(prompt)
            if response is None:
                continue
                
            # Validate format
            if not validate_gpt_response(response):
                #print(f"Invalid response format on attempt {attempt + 1}")
                continue
                
            try:
                result = json.loads(response)
                return FinalOutput(
                    user_nlp_query=result["user_nlp_query"],
                    reasonings=[
                        Thought(**thought) for thought in result["reasonings"]
                    ],
                    generated_sql_query=result["generated_sql_query"]
                )
            except Exception as e:
                #print(f"Error parsing response: {str(e)}")
                if attempt == max_retries - 1:
                    return FinalOutput(
                        user_nlp_query=question,
                        reasonings=[
                            Thought(
                                thought=f"Failed to parse response: {str(e)}",
                                helpful=False
                            )
                        ],
                        generated_sql_query="SELECT 1"
                    )
                continue
                
        except Exception as e:
            #print(f"Process error: {str(e)}")
            if attempt == max_retries - 1:
                return FinalOutput(
                    user_nlp_query=question,
                    reasonings=[
                        Thought(
                            thought=f"Error in process: {str(e)}",
                            helpful=False
                        )
                    ],
                    generated_sql_query="SELECT 1"
                )
            continue
    
    return FinalOutput(
        user_nlp_query=question,
        reasonings=[
            Thought(
                thought="Maximum retries exceeded",
                helpful=False
            )
        ],
        generated_sql_query="SELECT 1"
    )

############################################ SELF CORRECTION
def debuger(question,sql, predicted_class, schema_dict):
	if '"EASY"' in predicted_class:
		prompt_used = easy_prompt_maker(
                    question=question,
                    schema_dict=schema_dict
                )
	elif '"NON-NESTED"' in predicted_class:
		prompt_used = medium_prompt_maker(
                    question=question,
                    schema_dict=schema_dict
                )
	else:
		prompt_used = hard_prompt_maker(
                    question=question,
                    schema_dict=schema_dict
                )

	instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to check if the given SQLite SQL QUERY has any issues. If there are any issues, fix them and return the fixed SQLite QUERY in the output. If there are no issues, return the SQLite SQL QUERY as is in the output."
#### Background Information:
Relevant Schema Links:
{schema_links}
Prompt Used to Generate the Candidate SQLite SQL Query:
'''
{prompt_used}
'''
#### Use the following instructions for fixing the SQL QUERY: 
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT only when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only."""
	prompt = instruction.format(
       schema_links=schema_dict["schema_links"],
	   prompt_used=prompt_used
   ) + f"""
#### Question: {question}
#### SQLite SQL QUERY
{sql}
#### SQLite FIXED SQL QUERY
"""
	return prompt

def GPT4_debug(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream = False,
        temperature=0.0,
        #max_tokens=350,
        top_p = 1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop = ["#", ";","\n\n"]
    )
    return response.choices[0].message.content


def refine_query(question, sql, classification, schema_dict):
	debugged_SQL = None
	while debugged_SQL is None:
		try:
			debugged_SQL = GPT4_debug(debuger(question,sql, classification, schema_dict))
		except:
			time.sleep(3)
			pass
	try:
		return debugged_SQL.split('```sql', 1)[1]
	except:
		raise IndexError
		

############################################ HERE ENDS DIN-CHASE HYBRID
############################################ Compare CSV and processing

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

import pandas as pd
import re

def get_aggregate_columns(sql_query):
    """
    Extract resulting output column names of aggregate functions in the SQL query,
    handling duplicates and default naming conventions.
    """
    aggregate_functions = ["SUM", "AVG", "COUNT", "MAX", "MIN"]
    output_columns = []

    # Regex to match aggregate functions with optional aliasing
    pattern = rf"({'|'.join(aggregate_functions)})\((.*?)\)(?:\s+AS\s+([\w_]+))?"
    
    matches = re.findall(pattern, sql_query, re.IGNORECASE)
    function_counter = {}  # Track occurrences of each aggregate function
    
    for func, inner, alias in matches:
        func_lower = func.lower()
        if alias:  # Explicit alias defined
            output_columns.append(alias)
        else:  # No alias, use default naming conventions
            if func_lower not in function_counter:
                function_counter[func_lower] = 0
            else:
                function_counter[func_lower] += 1
            # Generate default name (e.g., sum, sum_1, sum_2, etc.)
            if function_counter[func_lower] == 0:
                output_columns.append(f"{func_lower}({inner.strip()})")  # Default naming for SQLite
            else:
                output_columns.append(f"{func_lower}({inner.strip()})_{function_counter[func_lower]}")  # Add suffix

    return output_columns

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
                    "schema": naive_schema_info # this is where the schema is entered
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
async def process_din_query(llm_query: Query):
    try: 
        schema_dict = global_vr.process_schema(llm_query.question)
        append_to_file(f"Schema Links for Question: {llm_query.question}\n{schema_dict}")
    except Exception as e:
        err_string = (f"Error in process_schema of Value Retrieval: {e}")
        print(err_string)
        append_to_file(err_string)
        raise e
    try:
        classification, class_reasoning = process_question_classification(llm_query.question, schema_dict)
        append_to_file(f"classification reasoning: {class_reasoning}")
        append_to_file(f"classification: {classification}")
    except Exception as e:
        err_string = (f"Error in process_question_classification of Classification: {e}")
        print(err_string)
        append_to_file(err_string)
        raise e
    try:
        process_thesql = process_question_sql(llm_query.question, classification, schema_dict)
        append_to_file(f"Thoughts: {process_thesql.reasonings}")
        append_to_file(f"process_thesql: {process_thesql}")
    except Exception as e:
        err_string = (f"Error in process_question_sql of SQL Generation: {e}")
        print(err_string)
        append_to_file(err_string)
        raise e
    try:
        final_output = refine_query(llm_query.question, process_thesql, classification, schema_dict)
        append_to_file(f"final_output: {final_output}")
    except Exception as e:
        err_string = (f"Error in refine_query of Self-Correction: {e}")
        print(err_string)
        append_to_file(err_string)
        raise e
    try:
        llm_csv = execute_sql(final_output.replace("```sql", "").replace("```", "").strip())
    except Exception as e:
        err_string = (f"Error Executing LLM-Generated SQL: {str(e)}")
        print(err_string)
        append_to_file(err_string)
        raise e
    return {
        "sql_query": final_output.replace("```sql", "").replace("```", "").strip(),
        "csv_results": llm_csv  # CSV data embedded as a JSON field
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
