# File to create OpenAI chatbot responses based on user queries

from typing import List

from chromadb import Collection
from ollama import Client
from openai import OpenAI

NUM_RESULTS = 5
MAX_HISTORY = 4  # Sets the number of previous messages to include in the history


def query_chatbot(query: str, index: Collection, model: str, openai_client: OpenAI, history: List[dict]) -> dict:
    """
    Retrieves context based on the user query and then generates a response from the OpenAI client.

    Args:
        query (str): User query from the frontend
        index (Collection): Chunked and embedded text to retrieve from
        model (str): The selected LLM to use for generating the response
        openai_client (OpenAI): OpenAI client to use for the chat response
        history (List[dict]): History of the chat session

    Returns:
        dict: The response to the user's query from the OpenAI model. Dictionary with "response" (str) and "sources" (List[str]).
    """
    full_query = update_query(query=query, client=openai_client, model=model, history=history)
    print(f"query={query}\nfull query={full_query}\n")
    context = retrieve_context(query=full_query, index=index)
    response = generate_response(context=context, client=openai_client, model=model, history=history)
    chat_output = compile_full_response(context=context, response=response)

    return chat_output


def update_query(query: str, model: str, client: OpenAI, history: List[dict]) -> str:
    """
    Update the user query based on the conversation context using the selected LLM

    Args:
        query (str): User query from frontend
        model (str): LLM to use to update the query
        client (OpenAI): The OpenAI model to use for generating the response
        history (List[dict]): Chat history, including the user query

    Returns:
        str: The Gen AI generated response to the user query
    """

    message = [
            {
                "role": "system",
                "content": f"Use the below user query and recent chat history to create an updated user query that will return relevant context \
                    from the article to answer their question. If the current user query is sufficient, just return the same query.\
                    Only return the updated user query and no additional text or explanation.\
                    BEGIN USER QUERY:\
                    {query}\
                    END USER QUERY"
            }
        ]

    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    return generate_completion(message=message, openai_client=client, model=model)


def retrieve_context(query: str, index: Collection) -> dict:
    """
    Retrieve relevant context from the DB based on the query

    Args:
        query (str): The query to return context about
        index (Collection): The collection of embedding text to retrieve context from

    Returns:
        dict: Retrieved context and metadata
    """

    return index.query(query_texts=[query], n_results=NUM_RESULTS)


def generate_response(context: dict, client: OpenAI, model: str, history: List[dict]) -> str:
    """
    Generate the response to the user query based on the supplied context, history, and user query.

    Args:
        context (dict): Retrieved context from source documents
        client (OpenAI): The OpenAI model to use for generating the response
        model (str): The LLM to use to generate the response
        history (List[dict]): Chat history, including the user query

    Returns:
        str: The Gen AI generated response to the user query
    """

    message = [
            {
                "role": "system",
                "content": f"You are an assistant that answers user questions based only on the supplied context. \
                Only answer using information in the supplied context.\
                If the context doesn't have the information needed to answer the question, just answer with 'I don't know the answer.'.\
                BEGIN CONTEXT:\
                {context['documents']}\
                END CONTEXT"
            }
        ]

    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    return generate_completion(message=message, openai_client=client, model=model)
    

def generate_completion(message: List[dict], openai_client: OpenAI, model: str) -> str:
    """
    Generate the chat completion for the input message

    Args:
        message (List[dict]): Input message with relevant history and/or context
        openai_client (OpenAI): The OpenAI model to use for generating the response
        model (str): The model name to use for completion

    Returns:
        str: Chat completion output message
    """

    if model == "gpt-4o-mini":
        completion = openai_client.chat.completions.create(
            model=model,
            messages=message,
            temperature=0.0,
            top_p=0.5
        )
        return completion.choices[0].message.content
    else:
        client = Client(host='http://host.docker.internal:11434')
        response = client.chat(
            model=model, messages=message, options={"temperature": 0.0, "top_p": 0.5}
        )

        return response.message.content


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
