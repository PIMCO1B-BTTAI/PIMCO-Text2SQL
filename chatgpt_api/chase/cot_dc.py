import openai
import os
import os
import time
import chat_prompt
from dotenv import load_dotenv
load_dotenv()

# Set API key
client = openai(api_key=os.environ.get("OPENAI_API_KEY"))

# Check is API key is configured
if not client.api_key:
    raise ValueError("OpenAI API key not configured")

# Create class to instantiate divide and conquer objectss
class ChaseDivideAndConquer:
    def __init__(self, few_shot_examples, db_schema):
        self.few_shot_examples = few_shot_examples
        self.db_schema = db_schema

    def generate_sub_questions(self, question, database):
        """
        Decompose original question into sub-questions.
        
        question: The original user question.
        database: The database schema.
        """
        prompt = f"Decompose the following question into a list of smaller sub-questions:\nQuestion: {question}\nDatabase: {database}"
        response = client.chat.completions.create(
						model="gpt-4o",
						messages=[{"role": "user", "content": prompt}],
						temperature=0.0,
						max_tokens=600,
						top_p = 1.0,
						frequency_penalty=0.0,
						presence_penalty=0.0,
					).choices[0].message.content


        sub_questions = response.split("\n")  # Assume model response is a list of sub-questions

        return sub_questions

    def generate_partial_sql(self, sub_question, context):
        """
        Generate a partial SQL query for each sub-question.
        
        :param sub_question: A single sub-question.
        :param context: Context is the combination of previous sub-questions and partial SQL queries.
        :return: The SQL query for this sub-question.
        """
        prompt = f"Given the following context and sub-question, generate a SQL query:\nContext: {context}\nSub-question: {sub_question}\nDatabase: {self.db_schema}"
        response = client.chat.completions.create(
						model="gpt-4o",
						messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
						max_tokens=600,
						top_p = 1.0,
						frequency_penalty=0.0,
						presence_penalty=0.0,
					).choices[0].message.content
        
        return response.strip()

    def assemble_final_sql(self, sub_questions, partial_sqls):
        """
        Assemble the final SQL query from the sub-queries and partial SQLs.
        
        sub_questions: List of sub-questions.
        partial_sqls: List of partial SQL queries corresponding to the sub-questions.
        return: Final assembled SQL query.
        """
        prompt = f"Given the following sub-questions and partial SQL queries, assemble the final SQL query:\nSub-questions: {sub_questions}\nPartial SQLs: {partial_sqls}\nDatabase: {self.db_schema}"
        response = openai.chat.completions.create(
                        model="gpt-4o",
						messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
						max_tokens=600,
						top_p = 1.0,
						frequency_penalty=0.0,
						presence_penalty=0.0,
        ).choices[0].message.content

        return response.strip()

    def generate_sql(self, user_question):
        """
        Main function to generate SQL query using Divide and Conquer CoT
        
        user_question: The original user question.
        return: The final SQL query
        """
        # Divide
        sub_questions = self.generate_sub_questions(user_question, self.db_schema)

        # Conquer
        partial_sqls = []
        context = []  # Keep track of sub-questions and SQL
        for sub_question in sub_questions:
            partial_sql = self.generate_partial_sql(sub_question, context)
            partial_sqls.append(partial_sql)
            context.append((sub_question, partial_sql))  # Update context with the current sub-question and SQL

        # Assemble
        final_sql = self.assemble_final_sql(sub_questions, partial_sqls)
        return final_sql


# Example usage:
if __name__ == "__main__":
    few_shot_examples = [
        # Set of human-annotated few-shot examples
        ## ADD HERE
    ]
    db_schema = chat_prompt.schema_info
    
    # Initialize the Divide and Conquer Text-to-SQL strategy
    example_nl_to_sql = ChaseDivideAndConquer(few_shot_examples, db_schema)
    
    user_question = "What is the total sales by region in the last quarter?"
    sql_query = example_nl_to_sql.generate_sql(user_question)
    
    print(f"Generated SQL Query: {sql_query}")
