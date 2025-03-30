# This file controls the UI action in the streamlit app

from typing import Tuple

from chromadb import Collection
from openai import OpenAI
import streamlit as st

from backend.data_prep import prepare_data
from backend.chatbot import query_chatbot


# Initialize DB and OpenAI Client at start only
@st.cache_resource
def init_function() -> Tuple[Collection, OpenAI]:
    """
    Initialize the backend. This includes ingesting data, connecting to the vector database, and setting up the OpenAI client.
    This only runs on app startup.

    Returns:
        Tuple[Collection, OpenAI]: A tuple with the embedded and chunked data and the OpenAI client.
    """
    index, openai_client = prepare_data()

    return index, openai_client


index, openai_client = init_function()

st.title("Flexible RAG Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Type in your question."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response and add to chat history
    with st.chat_message("assistant"):
        response = query_chatbot(
            query=prompt,
            index=index,
            openai_client=openai_client,
            history=st.session_state.messages,
        )   
        st.write(response["response"])

        # Get unique list of pages used (we can have multiple chunks used per page)
        unique_sources = list(dict.fromkeys(response["sources"]))
        
        # Display sources
        with st.expander("Sources"):
            for i, source in enumerate(unique_sources):
                st.write(f"{i+1}. {source}")
    
    st.session_state.messages.append({"role": "assistant", "content": response["response"]})

def clear_chat_history():
    st.session_state.messages = []

st.button(label="Clear History", key="chat_clear", on_click=clear_chat_history)
    
