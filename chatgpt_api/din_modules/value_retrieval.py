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
import nltk


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

        # Build vectorizer and LSH
        self.build_vectorizer_and_lsh(seed=lsh_seed)

        # Get schema relationships
        self.primary_keys, self.foreign_keys = self.discover_schema_relationships()

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
        # Define our primary keys and foreign keys here / needs edits (this is based on nport readme)
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

     
        foreign_keys = [# ACCESSION_NUMBER relationships (all link back to FUND_REPORTED_INFO)
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

            # HOLDING_ID relationships (all link back to FUND_REPORTED_HOLDING)
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
        # Find similar words in the schema with their similarity scores using p-stable LSH
        if not word:
            return []

        word = word.lower()
        print(f"\nDEBUG: Finding matches for '{word}'")

        word_vector = self.vectorizer.transform([word]).toarray()[0]
        candidate_indices = self.lsh.query(word_vector)
        print(f"Found {len(candidate_indices)} initial candidates")

        similarities = []
        for idx in candidate_indices:
            candidate_term = self.term_list[idx]
            candidate_vector = self.term_vectors[idx].toarray()[0]
            # Compute Euclidean distance
            dist = np.linalg.norm(word_vector - candidate_vector)
            sim = 1 / (1 + dist)
            similarities.append((candidate_term, sim))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Print top matches
        print(f"Found {len(similarities)} matches")
        for match, score in similarities[:5]: 
            print(f"  {match}: {score:.4f}")

        return similarities[:5]  # Return top 5 matches

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
        """Tokenize and lemmatize input text, removing stop words."""
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


if __name__ == "__main__":
    vr = ValueRetrieval(schema_path='chatgpt_api/schema.json')

    question = "Show me all funds with total asset over 1 billion"
    result = vr.process_question(question)

    from pprint import pprint
    pprint(result)
