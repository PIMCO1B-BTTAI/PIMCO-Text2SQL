# PIMCO

### Set up database before running app:
1. open PIMCO1B_Database_2.ipynb
2. run all (this should create a nport.db in your sqlite folder)
3. proceed to run app

### How to run app:
1. Open bash terminal, run 
```uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000```
2. Open a new bash terminal without closing the first, run 
```streamlit run chatbot.py```
3. App should pop up in browser, else click Local URL in terminal
4. Chat with the Chatbot!

### First commit:
To run this for the first time
1. open a bash terminal
4. run `pip install -r requirements.txt` in the virtual environment
5. set up openAI API Key:  
    on Linux/MacOS/Unix Terminals run `export OPENAI_API_KEY='your_openai_api_key_here'`  
    on Windows run `set OPENAI_API_KEY=your_openai_api_key_here`  
6. run `streamlit run chatbot.py`
7. open a new bash terminal, run `uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000`




