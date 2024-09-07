# PIMCO

### Dev Production Notes:
Below are what we plan to do at the moment, and more things might be added; we will properly create story boards on notion for them later.
1. Datafile cleaning and structuring \(some fields are sparse\)
2. Database build \(and a way to provide database schema information to the LLM\)
3. Fine-tuning the LLM model using OpenAI's CLI tool
4. Maintaining context across chat
5. Autonomous error correction by the LLM 


### First commit:
For the first commit, because no database has been set up, `api.py` and `streamlit_chatbot.py` are very crude prototypes that do not function together as intended. To see the chatbot front end, follow these steps.
1. open a bash terminal
2. create and activate a virtual environment
4. run `pip install -r requirements.txt` in the virtual environment
5. run `streamlit run streamlit_chatbot.py`

Sending a message to the chatbot does send the HTTP request to api.py correctly, but the prompt can't be routed to OpenAI API because we don't have a key yet, and the async function `process_query()` gets stuck at line `sql_query = generate_sql(query.question)`
