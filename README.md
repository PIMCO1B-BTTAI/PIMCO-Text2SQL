# Extracting Sturctured Information Using LLM

### Provisional Writeup Slide Deck

https://drive.google.com/file/d/16NBGP9QB7r07YMzmxbgcXHkuAwh0oOit/view?usp=sharing


### Setup
1. Follow the `MASTER_SETUP_SCRIPT.ipynb` in `setup/`
2. set up openAI API Key:  
    on Linux/MacOS/Unix Terminals run `export OPENAI_API_KEY='your_openai_api_key_here'`  
    on Windows run `set OPENAI_API_KEY=your_openai_api_key_here`  

### How to run demo app:
1. Open bash terminal, run 
```uvicorn chatgpt_api.api:app --host 0.0.0.0 --port 8000```
2. Open a new bash terminal without closing the first, run 
```streamlit run chatbot.py```
3. App should pop up in browser, else click Local URL in terminal
4. Chat with the Chatbot!




