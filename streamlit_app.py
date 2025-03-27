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

st.title("RAG Chatbot")

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
    st.session_state.messages.append({"role": "assistant", "content": st.write(response["response"] + "\n\n**Sources:**\n\n" + str(response["sources"]))})
