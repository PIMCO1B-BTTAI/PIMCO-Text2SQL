#----------example of a query (execution) plan prompt----------
""" Database Info
{DATABASE_SCHEMA}
**************************
Answer Repeating the question and evidence, and generating the SQL with a query plan.
**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany?
**Evidence**: Thai restaurant refers to food_type = ’thai’; San Pablo Ave Albany refers to street_name
= ’san pablo ave’ AND T1.city = ’albany’
**Query Plan**:
** Preparation Steps:**
1. Initialize the process: Start preparing to execute the query.
2. Prepare storage: Set up storage space (registers) to hold temporary results, initializing them to NULL.
3. Open the location table: Open the location table so we can read from it.
4. Open the generalinfo table: Open the generalinfo table so we can read from it.
** Matching Restaurants:**
1. Start reading the location table: Move to the first row in the location table.
2. Check if the street matches: Look at the street_name column of the current row in location. If it’s not
"san pablo ave," skip this row.
3. Identify the matching row: Store the identifier (row ID) of this location entry.
4. Find the corresponding row in generalinfo: Use the row ID from location to directly find the matching
row in generalinfo.
5. Check if the food type matches: Look at the food_type column in generalinfo. If it’s not "thai," skip
this row.
6. Check if the city matches: Look at the city column in generalinfo. If it’s not "albany," skip this row.
** Counting Restaurants:**
1. Prepare to count this match: If all checks pass, prepare to include this row in the final count.
2. Count this match: Increment the count for each row that meets all the criteria.
3. Move to the next row in location: Go back to the location table and move to the next row, repeating
the process until all rows are checked.
4. Finalize the count: Once all rows have been checked, finalize the count of matching rows.
5. Prepare the result: Copy the final count to prepare it for output.
** Delivering the Result:**
1. Output the result: Output the final count, which is the number of restaurants that match all the
specified criteria.
2. End the process: Stop the query execution process.
3. Setup phase: Before starting the actual query execution, the system prepares the specific values it will
be looking for, like "san pablo ave," "thai," and "albany."
**Final Optimized SQL Query:**
SELECT COUNT(T1.id_restaurant) FROM generalinfo AS T1 INNER JOIN location AS T2
ON T1.id_restaurant = T2.id_restaurant WHERE T1.food_type = ’thai’ AND T1.city = ’albany’ AND
T2.street_name = ’san pablo ave’ """


import openai
import json

# Initialize OpenAI API (ChatGPT)
openai.api_key = "OPENAI_API_KEY"  # Ensure you replace this with your OpenAI API key.

# Define a sample schema for your database (this can be dynamically loaded or adjusted based on your project)
DATABASE_SCHEMA = {
    "table1": ["column1", "column2", "column3"],
    "table2": ["column1", "column2", "column3"]
}

# Function to parse the user query and extract the relevant keywords
def parse_query(natural_query):
    """
    Parse the user query into key-value pairs representing the filters and criteria.
    Uses a simple keyword matching method or ChatGPT to identify entities.
    """
    keywords = {}
    # Use ChatGPT to extract entities from the natural language query
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Extract entities from the following question:\n{natural_query}",
        max_tokens=150
    )
    
    # Simple example: keywords extraction from the query (could be more sophisticated)
    extracted_keywords = response.choices[0].text.strip().split(",")  # Assuming comma-separated values returned
    for keyword in extracted_keywords:
        # Further logic to match keywords to schema columns
        if "condition1" in keyword.lower():
            keywords["column1"] = "condition1_value"
        if "condition2" in keyword.lower():
            keywords["column2"] = "condition2_value"
        if "condition3" in keyword.lower():
            keywords["column3"] = "condition3_value"
    
    return keywords

# Function to generate evidence (SQL conditions) from parsed query
def generate_evidence(parsed_query):
    """
    Generate the SQL conditions for the WHERE clause based on parsed query.
    """
    evidence_parts = []
    if "column1" in parsed_query:
        evidence_parts.append(f"column1 = '{parsed_query['column1']}'")
    if "column2" in parsed_query:
        evidence_parts.append(f"column2 = '{parsed_query['column2']}'")
    if "column3" in parsed_query:
        evidence_parts.append(f"column3 = '{parsed_query['column3']}'")
    return " AND ".join(evidence_parts)

# Function to generate the query execution plan (Chain-of-Thought)
def generate_query_plan(parsed_query):
    """
    Generate the query plan (CoT) for the SQL query using a step-by-step process.
    """
    steps = []
    
    # ChatGPT to describe the process
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Describe the process of executing the following SQL query step by step:\nExtract the tables and columns used from this query: \n{parsed_query}",
        max_tokens=300
    )
    
    # Generate a step-by-step explanation based on the response
    steps.append(response.choices[0].text.strip())
    
    return "\n".join(steps)

# Function to generate the final SQL query using ChatGPT
def generate_sql_query(parsed_query):
    """
    Generate the final SQL query using ChatGPT.
    """
    conditions = generate_evidence(parsed_query)
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Generate an SQL query for the following conditions:\n{conditions}\nUsing the tables and columns in the database schema: {json.dumps(DATABASE_SCHEMA)}",
        max_tokens=150
    )
    
    sql_query = response.choices[0].text.strip()
    return sql_query

# Main function to process the user's query
def process_query(natural_query):
    """
    Process the user query, generate the plan, evidence, and SQL query.
    """
    parsed_query = parse_query(natural_query)  # Parse query to extract the entities
    evidence = generate_evidence(parsed_query)  # Generate evidence for the WHERE clause
    query_plan = generate_query_plan(parsed_query)  # Generate query execution plan (CoT)
    sql_query = generate_sql_query(parsed_query)  # Generate final SQL query

    return {
        "Question": natural_query,
        "Parsed Query": parsed_query,
        "Evidence": evidence,
        "Query Plan": query_plan,
        "SQL Query": sql_query
    }

# Example Usage
if __name__ == "__main__":
    user_query = "How many items are available in stock for condition1_value and condition2_value?"
    results = process_query(user_query)

    print("Question:", results["Question"])
    print("\nParsed Query:", results["Parsed Query"])
    print("\nEvidence:", results["Evidence"])
    print("\nQuery Plan:\n", results["Query Plan"])
    print("\nFinal SQL Query:\n", results["SQL Query"])
