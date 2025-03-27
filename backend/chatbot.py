# File to create OpenAI chatbot responses based on user queries

from typing import List

from chromadb import Collection
from openai import OpenAI

NUM_RESULTS = 5


def query_chatbot(query: str, index: Collection, openai_client: OpenAI, history: List[dict]) -> str:
    """
    Retrieves context based on the user query and then generates a response from the OpenAI client.

    Args:
        query (str): User query from the frontend
        index (Collection): Chunked and embedded text to retrieve from
        openai_client (OpenAI): OpenAI client to use for the chat response
        history (List[dict]): History of the chat session

    Returns:
        str: The response to the user's query from the OpenAI model
    """
    context = retrieve_context(query=query, index=index)
    response = generate_response(context=context, client=openai_client, query=query, history=history)
    chat_output = compile_full_response(context=context, response=response)

    return chat_output


def retrieve_context(query: str, index: Collection) -> dict:

    context = index.query(query_texts=[query], n_results=NUM_RESULTS)

    return context


def generate_response(context: dict, client: OpenAI, query: str, history: List[dict]) -> str:
    """
    Generate the response to the user query based on the supplied context, history, and user query.

    Args:
        context (dict): Retrieved context from source documents
        client (OpenAI): The OpenAI model to use for generating the response
        query (str): User query from frontend
        history (List[dict]): Chat history

    Returns:
        str: The Gen AI generated response to the user query
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an assistant that helps answer user questions based on the supplied context. Only answer using the below context. \
                If the context doesn't have the information needed to answer the question, just answer with 'I don't know the answer.'.\
                BEGIN CONTEXT:\
                {context['documents']}\
                END CONTEXT",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"BEGIN USER QUERY:\
                {query}\
                END USER QUERY",
                    }
                ],
            },
        ],
    )

    return completion.choices[0].message.content


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
        filename = (context["metadatas"][0][i]["filename"]).split("\\")[-1]
        page = context["metadatas"][0][i]["page_number"]
        score = round(context["distances"][0][i], 3)
        sources.append(f'{filename} page {page} with cosine similarity={score}')
                   

    return {"sources": sources, "response": response}
