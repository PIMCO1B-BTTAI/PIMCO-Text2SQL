# PIMCO

### Set up database before running app:
1. Download all quarters' NPORT dataset (`.zip` files) and drop them into `data/` folder in your local directory
2. run `python extract_data_zips.py` in `data/` folder to extract all of them
3. run PIMCO1B_Database_2.ipynb in main folder, all cells (this should create a nport.db in your sqlite folder)
Then, proceed to run app below

### First Run:
To run this for the first time
1. open a bash terminal
4. run `pip install -r requirements.txt` in the virtual environment or your global python environment
5. set up openAI API Key:  
    on Linux/MacOS/Unix Terminals run `export OPENAI_API_KEY='your_openai_api_key_here'`  
    on Windows run `set OPENAI_API_KEY=your_openai_api_key_here`  
6. run `streamlit run chatbot.py`
7. open a new bash terminal, run `uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000`

### How to run app:
1. Open bash terminal, run 
```uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000```
2. Open a new bash terminal without closing the first, run 
```streamlit run chatbot.py```
3. App should pop up in browser, else click Local URL in terminal
4. Chat with the Chatbot!




