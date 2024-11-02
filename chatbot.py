import streamlit as st
import requests
import json
import pandas as pd
import io

# Page configuration
st.set_page_config(
    page_title="Financial Data Chatbot",
    page_icon="💬",
    layout="wide",
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

local_css("style.css")

# Hide Streamlit's default menu and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Title and description
st.title("💬 Financial Data Chatbot")
st.markdown("Ask questions about financial data and get SQL queries with results.")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display chat messages
chat_placeholder = st.container()

with chat_placeholder:
    for i, msg in enumerate(st.session_state['messages']):
        if msg['role'] == 'user':
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)

# Add a spacer to push the input area to the bottom
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# Input area at the bottom
with st.form(key='input_form', clear_on_submit=True):
    st.markdown('<div class="input-container">', unsafe_allow_html=True)

    # Arrange input and button side by side
    input_col, button_col = st.columns([10, 1])

    with input_col:
        user_input = st.text_input(
            "Your Message",
            placeholder="Type your message here...",
            label_visibility='collapsed'
        )

    with button_col:
        submit_button = st.form_submit_button(label="➤")

    st.markdown('</div>', unsafe_allow_html=True)
    
    ### THIS IS WHERE USER INPUT IS PROCESSED IN BACKEND
    if submit_button and user_input:
        # Add user message to session state
        st.session_state['messages'].append({'role': 'user', 'content': user_input})

        # Process assistant response
        with st.spinner('💡 Thinking... Please wait...'):
            # Send request to backend
            try:
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"question": user_input}
                )
                response.raise_for_status()
                result = response.json()
                sql_query = result.get('sql_query', 'No SQL query generated.')

                query_results = result.get('csv_results','')

                # Convert results to DataFrame
                if query_results:
                    df = pd.read_csv(io.StringIO(query_results))
                    df_html = df.to_html(index=False, classes='result-table', escape=False)
                    #df_html = "TEST_SQL_RESULTS"
                else:
                    df_html = "<p>No results found.</p>"

                # Format assistant's response
                #assistant_message = str(sql_query) 
                assistant_message = f"**SQL Query:**\n```sql\n{sql_query}\n```\n**Results:**\n{df_html}"

                # Add assistant message to session state
                st.session_state['messages'].append({'role': 'assistant', 'content': assistant_message})

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
                st.session_state['messages'].append({'role': 'assistant', 'content': f"Error: {e}"})

        # Rerun the script to refresh the chat messages
        st.rerun()
