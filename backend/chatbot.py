# File to create OpenAI chatbot responses based on user queries

from typing import List

from chromadb import Collection
from ollama import Client
from openai import OpenAI

NUM_RESULTS = 5
MODEL_TYPE = "local" # "openai" or "local"
LOCAL_MODEL_NAME = "llama3.2" # Name of the local model inside the models directory, leave as "" if using openai
MAX_HISTORY = 4  # Sets the number of previous messages to include in the history


def query_chatbot(query: str, index: Collection, openai_client: OpenAI, history: List[dict]) -> dict:
    """
    Retrieves context based on the user query and then generates a response from the OpenAI client.

    Args:
        query (str): User query from the frontend
        index (Collection): Chunked and embedded text to retrieve from
        openai_client (OpenAI): OpenAI client to use for the chat response
        history (List[dict]): History of the chat session

    Returns:
        dict: The response to the user's query from the OpenAI model. Dictionary with "response" (str) and "sources" (List[str]).
    """
    context = retrieve_context(query=query, index=index)
    response = generate_response(context=context, client=openai_client, history=history)
    chat_output = compile_full_response(context=context, response=response)

    return chat_output


def retrieve_context(query: str, index: Collection) -> dict:

    context = index.query(query_texts=[query], n_results=NUM_RESULTS)

    return context


def generate_response(context: dict, client: OpenAI, history: List[dict]) -> str:
    """
    Generate the response to the user query based on the supplied context, history, and user query.

    Args:
        context (dict): Retrieved context from source documents
        client (OpenAI): The OpenAI model to use for generating the response
        history (List[dict]): Chat history, including the user query

    Returns:
        str: The Gen AI generated response to the user query
    """

    message = [
            {
                "role": "system",
                "content": f"You are an assistant that answers user questions based only on the supplied context. Only answer using information in the supplied context.\
                If the context doesn't have the information needed to answer the question, just answer with 'I don't know the answer.'.\
                BEGIN CONTEXT:\
                {context['documents']}\
                END CONTEXT"
            }
        ]

    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    if MODEL_TYPE == "openai":
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=message,
        )
        return completion.choices[0].message.content
    elif MODEL_TYPE == "local":
        client = Client(host='http://host.docker.internal:11434')
        response = client.chat(model=LOCAL_MODEL_NAME, messages=message)

        return response.message.content
    else:
        print("MODEL_TYPE must be openai or local")
        return ""


def compile_full_response(context: dict, response: str) -> dict:
    """
    Compile the full response with sources

    Args:
        context (dict): _description_
        response (str): _description_

    Returns:
        dict: _description_
    """

    sources = []

    for i in range(len(context["ids"][0])):
        filename = (context["metadatas"][0][i]["filename"]).split("/")[-1]
        page = context["metadatas"][0][i]["page_number"]
        score = round(context["distances"][0][i], 3)
        sources.append(f'{filename} page {page} with cosine similarity={score}')
                   

    return {"sources": sources, "response": response}
