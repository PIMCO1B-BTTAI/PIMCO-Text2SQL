from itertools import combinations
import sqlite3
import openai

def execute_query(query, database_path):
    """
    Executes a SQL query on the SQLite database and returns the result.

    Parameters:
        query (str): The SQL query to execute.
        database_path (str): Path to the SQLite database file.

    Returns:
        result (list): The result of the SQL query as a list of tuples.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results
        result = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        return result
    except Exception as e:
        print(f"Error executing query: {query}\nError: {e}")
        return None

def get_schema_union(query1, query2, database_path):
    """
    Constructs the union of schemas used in two SQL queries.

    Parameters:
        query1 (str): The first SQL query.
        query2 (str): The second SQL query.
        database_path (str): Path to the SQLite database file.

    Returns:
        schema_union (dict): A dictionary with table names as keys and lists of column names as values.
    """
    def extract_tables_and_columns(query, database_path):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Extract table names using PRAGMA table_info
            tables = []
            columns = {}
            
            # Basic heuristic to extract table names (assumes FROM <table> clause)
            for word in query.split():
                if word.upper() == "FROM":
                    table_name = query.split()[query.split().index(word) + 1]
                    tables.append(table_name)
            
            # Get schema information for each table
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                schema_info = cursor.fetchall()
                columns[table] = [col[1] for col in schema_info]
            
            # Close the connection
            conn.close()
            
            return columns
        except Exception as e:
            print(f"Error extracting schema: {e}")
            return {}

    # Extract columns for both queries
    schema1 = extract_tables_and_columns(query1, database_path)
    schema2 = extract_tables_and_columns(query2, database_path)

    # Construct the union of schemas
    schema_union = {}
    for table in set(schema1.keys()).union(schema2.keys()):
        schema_union[table] = list(set(schema1.get(table, []) + schema2.get(table, [])))

    return schema_union

class GPTSelectionModel:
    def __init__(self, api_key, model_name="gpt-4"):
        self.api_key = api_key
        self.model_name = model_name
        openai.api_key = self.api_key

    def predict(self, schema_union, question, hint, candidate1, candidate2):
        """
        Uses GPT-4 to compare two SQL candidate queries and decide which one is better.

        Parameters:
            schema_union (str): Textual description of the schema union.
            question (str): The user question.
            hint (str): Optional hint for the comparison.
            candidate1 (str): The first candidate SQL query.
            candidate2 (str): The second candidate SQL query.

        Returns:
            str: "ci" if candidate1 is better, "cj" if candidate2 is better.
        """
        prompt = (
            f"User question: {question}\n"
            f"Hint: {hint}\n"
            f"Schema union: {schema_union}\n"
            f"Candidate 1: {candidate1}\n"
            f"Candidate 2: {candidate2}\n"
            "Which candidate query is more likely to be correct? Respond with 'Candidate 1' or 'Candidate 2' "
            "based on the accuracy, relevance, and correctness of the SQL queries."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in SQL and database query evaluation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.0  # Use deterministic output for consistent decisions
            )

            # Extract the decision from the response
            decision = response.choices[0].message["content"].strip()

            if "Candidate 1" in decision:
                return "ci"
            elif "Candidate 2" in decision:
                return "cj"
            else:
                print("Warning: Unexpected response from the LLM:", decision)
                return None
        except Exception as e:
            print(f"Error in GPTSelectionModel.predict: {e}")
            return None

def select_best_query(candidates, question, hint, database, selection_model):
    # Step 1: Initialize the score ri for each candidate query to zero
    scores = {candidate: 0 for candidate in candidates}

    # Step 2: Generate all possible pairs of candidates (k = 2)
    candidate_pairs = list(combinations(candidates, 2))

    # Step 3: Evaluate each pair using the selection model
    for ci, cj in candidate_pairs:
        # Execute the queries to get their results
        result_ci = execute_query(ci, database)
        result_cj = execute_query(cj, database)

        if result_ci == result_cj:
            # Arbitrarily choose ci as the winner if the execution results match
            scores[ci] += 1
        else:
            # Construct the union of schemas used by ci and cj
            schema_union = get_schema_union(ci, cj, database)
            
            # Use the selection model to decide the winner
            winner = selection_model.predict(schema_union, question, hint, ci, cj)
            
            # Increment the score of the chosen winner
            if winner == "ci":
                scores[ci] += 1
            else:
                scores[cj] += 1

    # Step 4: Select the candidate with the highest cumulative score
    best_query = max(scores, key=scores.get)

    return best_query

#To call the select_best_query method using gpt-4 as the selection model
api_key = "your_openai_api_key" # Define OpenAI API key

# Initialize the GPT-based selection model
gpt_selection_model = GPTSelectionModel(api_key)

# Define the candidates, question, and hint
candidates = ["The candidates results from last step"]
question = "The question we are asking"
hint = "Hint for the query like 'Focus on returning the names only.'"
database_path = "Our path to SQLite database"

# Find the best query
best_query = select_best_query(candidates, question, hint, database_path, gpt_selection_model)
print("Best Query:", best_query)