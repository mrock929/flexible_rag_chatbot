# This file controls the UI action in the streamlit app

from sqlite3 import Connection
from typing import Tuple, List

from chromadb import Collection
import streamlit as st

from backend.data_prep import prepare_data, get_available_models
from backend.chatbot import query_chatbot
from backend.data_tracking import manage_tracking_db, update_entry_with_feedback


@st.cache_resource
def init_function() -> Tuple[Collection, List[str], Connection]:
    """
    Initialize the backend. This includes ingesting data, connecting to the vector database, and connecting to the data tracking database.
    This only runs on app startup.

    Returns:
        Tuple[Collection, List[str]]: A tuple with the DB containing the embedded and chunked data, the list of available models, and the database cursor for the data tracking db.
    """
    index = prepare_data()
    model_list = get_available_models()
    connection = manage_tracking_db()

    return index, model_list, connection

def clear_chat_history():
    """Clear the chat history"""
    st.session_state.messages = []

def feedback_button_good():
    """Update the most recent entry with positive user feedback"""
    if len(st.session_state.messages) > 1:
        update_entry_with_feedback(connection=connection, is_good=True)
    else:
        raise ValueError("Please use the chatbot before providing feedback on a response. Refresh the page to try again.")
    
def feedback_button_bad():
    """Update the most recent entry with negative user feedback"""
    if len(st.session_state.messages) > 1:
        update_entry_with_feedback(connection=connection, is_good=False)
    else:
        raise ValueError("Please use the chatbot before providing feedback on a response. Refresh the page to try again.")


index, model_list, connection = init_function()

st.title("Flexible RAG Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Manage main chat area
if prompt := st.chat_input("Ask a question like, 'What is this article about?' or 'What is the HER-2/neu gene?'"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response and add to chat history
    with st.chat_message("assistant"):
        response = query_chatbot(
            query=prompt,
            index=index,
            model=st.session_state.model,
            history=st.session_state.messages,
            connection=connection,
            is_test=False
        )   
        st.write(response["response"])

        # Get unique list of pages used (we can have multiple chunks used per page)
        unique_sources = list(dict.fromkeys(response["sources"]))
        
        # Display sources
        with st.expander("Sources"):
            for i, source in enumerate(unique_sources):
                st.write(f"{i+1}. {source}")
    
    st.session_state.messages.append({"role": "assistant", "content": response["response"]})

# Create and manage sidebar
with st.sidebar:
    st.session_state.model = st.selectbox("Model Selection", model_list)
    st.button(label="Clear History", key="chat_clear", on_click=clear_chat_history)
    st.header("Model Response Feedback")
    st.button(label="Good", key="good_feedback", on_click=feedback_button_good)
    st.button(label="Bad", key="bad_feedback", on_click=feedback_button_bad)
