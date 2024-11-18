from openai import OpenAI
import json
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from Levenshtein import distance
from datasketch import MinHash, MinHashLSH

class ValueRetriever:
    def __init__(self, schema_path: str = 'chatgpt_api/schema.json'):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Load schema
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Initialize LSH - locality sensitive hashing
        self.lsh = MinHashLSH(threshold=0.5, num_perm=128)
        self.minhashes = {}
        
        # Build LSH index from schema
        self._build_lsh_index()
        
    def _build_lsh_index(self):
        # Build lsh from the schema columns
        for table in self.schema.get('tables', []):
            table_schema = table.get('tableSchema', {})
            
            for column in table_schema.get('columns', []):
                word = column['name'].lower()
                minhash = MinHash(num_perm=128)
                
                for i in range(len(word) - 2):
                    minhash.update(word[i:i+3].encode('utf-8'))
                
                self.minhashes[word] = minhash
                self.lsh.insert(word, minhash)

    def find_similar_words(self, word: str) -> List[Tuple[str, float]]:
        # This is called after LLM performs keyword extraction
        word = word.lower()
        
        query_minhash = MinHash(num_perm=128)
        for i in range(len(word) - 2):
            query_minhash.update(word[i:i+3].encode('utf-8'))
        
        candidates = self.lsh.query(query_minhash)
        
        similarities = []
        for candidate in candidates:
            sim = 1 - distance(word, candidate) / max(len(word), len(candidate))
            if sim > 0.5:  # Similarity threshold here
                similarities.append((candidate, sim))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True) # Ranking of similar words in schema

    def extract_keywords(self, question: str) -> Dict:
        system_prompt = """You are an expert financial data analyst specializing in natural language understanding.
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

        3. Return only a JSON object with these categories, no explanation needed."""

        few_shot_examples = """
        Example Question: "Show me BlackRock funds with total assets over 1 billion managed in New York"
        {
            "keywords": ["funds", "assets", "managed"],
            "keyphrases": ["total assets"],
            "named_entities": ["BlackRock", "New York"],
            "numerical_values": ["1 billion"]
        }

        Example Question: "List all registrants with more than 10 mutual funds and net assets above 500M"
        {
            "keywords": ["registrants", "funds", "assets"],
            "keyphrases": ["mutual funds", "net assets"],
            "named_entities": [],
            "numerical_values": ["10", "500M"]
        }

        Example Question: "Which PIMCO funds were registered between 2020 and 2023 with California addresses?"
        {
            "keywords": ["funds", "registered", "addresses"],
            "keyphrases": ["PIMCO funds"],
            "named_entities": ["PIMCO", "California"],
            "numerical_values": ["2020", "2023"]
        }"""

        user_prompt = f"""Analyze this financial question and extract key components:

        Question: "{question}"

        Return a JSON object with the extracted components following the same format as the examples."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": few_shot_examples + "\n" + user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def process_question(self, question: str) -> Dict:
        # Extract keywords using LLM
        extracted_info = self.extract_keywords(question)
        
        # Find similar words using LSH we did on database schema
        similar_matches = {}
        
        # Process individual keywords
        for keyword in extracted_info['keywords']:
            similar_matches[keyword] = self.find_similar_words(keyword)
        
        # Process words in keyphrases
        for keyphrase in extracted_info['keyphrases']:
            words = keyphrase.split()
            for word in words:
                if word not in similar_matches:
                    similar_matches[word] = self.find_similar_words(word)
        
        return {
            "extracted_info": extracted_info,
            "similar_matches": similar_matches
        }
