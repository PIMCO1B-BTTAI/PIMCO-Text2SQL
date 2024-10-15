# PIMCO

### How to run app:
1. Open bash terminal, run 
```uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000```
2. Open a new bash terminal without closing the first, run 
```streamlit run chatbot.py```
3. App should pop up in browser, else click Local URL in terminal
4. Chat with the Chatbot!

### Latest Commit:
Added File: **chatbot.py**
- Modified version of streamlit_chatbot.py
- streamlit_chatbot.py is kept for backup
- Modified/simplified HTTP Request response parsing for phase 1 NL_to_SQL; will revert modifications to more complex HTTP Request response parsing and processing for phase 2 SQL_to_Data
\\

Deleted File: **api.py**
- Content was transferred to new api file "api - with schema.py" and is deprecated

\\

Modified File: **api - with schema.py** (now **"api.py"**)
- Deleted whitespace from name for better references 
- Modified @app.post("/query") route, because only calls to OpenAI API is made; database yet to be connected   




### First commit:
For the first commit, because no database has been set up, `api.py` and `streamlit_chatbot.py` are very crude prototypes that do not function together as intended. To see the chatbot front end, follow these steps.
1. open a bash terminal
2. create a virtual environment (python -m venv env)
3. activate the virtual environment (source env/bin/activate)
4. run `pip install -r requirements.txt` in the virtual environment
5. set up openAI API Key:  
    on Linux/MacOS run `export OPENAI_API_KEY='your_openai_api_key_here'`  
    on Windows run `set OPENAI_API_KEY=your_openai_api_key_here`  
6. run `streamlit run streamlit_chatbot.py`

Sending a message to the chatbot does send the HTTP request to api.py correctly, but the prompt can't be routed to OpenAI API because we don't have a key yet, and the async function `process_query()` gets stuck at line `sql_query = generate_sql(query.question)`


