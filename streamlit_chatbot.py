import streamlit as st
import requests
import json

st.set_page_config(page_title="PIMCO Financial Data Chatbot", layout="wide")

# Custom CSS for a modern look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTextInput > div > div > input {
        background-color: #f7f7f7;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: #ffffff;
    }
    .chat-message.bot {
        background-color: #475063;
        color: #ffffff;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .message {
        width: 80%;
    }
</style>
""", unsafe_allow_html=True)

st.title("PIMCO Financial Data Chatbot")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send request to FastAPI backend
    response = requests.post("http://localhost:8000/query", json={"question": prompt})
    if response.status_code == 200:
        result = response.json()
        sql_query = result['sql_query']
        query_results = result['results']

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(f"Here's the SQL query I generated:")
            st.code(sql_query, language="sql")
            st.markdown("And here are the results:")
            st.json(query_results)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": f"SQL Query: {sql_query}\n\nResults: {json.dumps(query_results)}"})
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

# Sidebar for additional options or information
with st.sidebar:
    st.header("About")
    st.markdown("This chatbot uses AI to generate SQL queries based on your questions about PIMCO's financial data.")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()