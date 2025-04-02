# File to create OpenAI chatbot responses based on user queries

from datetime import datetime, timezone
from sqlite3 import Connection
from typing import List, Tuple

from chromadb import Collection
from ollama import Client

from .data_tracking import add_tracking_entry

NUM_RESULTS = 5  # Sets the number of chunks to return as context to the LLM
MAX_HISTORY = 4  # Sets the number of previous messages to include in the history


def query_chatbot(query: str, index: Collection, model: str, history: List[dict], connection: Connection, is_test: bool) -> dict:
    """
    Retrieves context based on the user query and then generates a response.

    Args:
        query (str): User query from the frontend
        index (Collection): Chunked and embedded text to retrieve from
        model (str): The selected LLM to use for generating the response
        history (List[dict]): History of the chat session
        connection (sqlite3.Connection): Valid sqlite3 connection for the database
        is_test (bool): True if test suite is running, False otherwise. This is to avoid saving all test queries in data tracking db

    Returns:
        dict: The response to the user's query from the model. Dictionary with "response" (str) and "sources" (List[str]).
    """
    retrieval_query = update_query(query=query, model=model, history=history)
    print(f"query={query}\nfull query={retrieval_query}\n")
    context = retrieve_context(query=retrieval_query, index=index)
    response, full_query = generate_response(context=context, model=model, history=history)
    chat_output = compile_full_response(context=context, response=response)
    if not is_test:
        time_now = str(datetime.now(timezone.utc))
        add_tracking_entry(connection=connection, query_timestamp=time_now, user_query=query, retrieval_query=retrieval_query, full_query=full_query, llm_response=response, sources=chat_output["sources"])

    return chat_output


def update_query(query: str, model: str, history: List[dict]) -> str:
    """
    Update the user query based on the conversation context using the selected LLM

    Args:
        query (str): User query from frontend
        model (str): LLM to use to update the query
        history (List[dict]): Chat history, including the user query

    Returns:
        str: The Gen AI generated response to the user query
    """

    message = [
            {
                "role": "system",
                "content": f"Use the below user query, article abstract, and recent chat history to create an updated user query that will return relevant context \
                    from the article to answer their question. If the current user query is sufficient, just return the same query.\
                    BEGIN USER QUERY:\
                    {query}\
                    END USER QUERY\
                    BEGIN ARTICLE ABSTRACT:\
                    The HER-2/neu oncogene is a member of the erbB-like \
                    oncogene family, and is related to, but distinct from, the \
                    epidermal growth factor receptor. This gene has been \
                    shown to be amplified in human breast cancer cell lines. \
                    In the current study, alterations of the gene in 189 \
                    primary human breast cancers were investigated. HER-2/ \
                    neu was found to be amplified from 2- to greater than 20- \
                    fold in 30% of the tumors. Correlation of gene amplification \
                    with several disease parameters was evaluated. Amplification \
                    of the HER-2/neu gene was a significant predictor \
                    of both overall survival and time to relapse in \
                    patients with breast cancer. It retained its significance \
                    even when adjustments were made for other known \
                    prognostic factors. Moreover, HER-2/neu amplification \
                    had greater prognostic value than most currently used \
                    prognostic factors, incuding hormonal-receptor status, \
                    in lymph node-positive disease. These data indicate that \
                    this gene may play a role in the biologic behavior and/or \
                    pathogenesis of human breast cancer.\
                    END ARTICLE ABSTRACT\
                    Only return the updated user query and no additional text, explanation, or thought process."
            }
        ]

    # Add chat history
    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    return generate_completion(message=message, model=model)


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


def generate_response(context: dict, model: str, history: List[dict]) -> Tuple[str, str]:
    """
    Generate the response to the user query based on the supplied context, history, and user query.

    Args:
        context (dict): Retrieved context from source documents
        model (str): The LLM to use to generate the response
        history (List[dict]): Chat history, including the user query

    Returns:
        Tuple[str, str]: The Gen AI generated response to the user query and the full query sent to the LLM
    """

    message = [
            {
                "role": "system",
                "content": f"You are an assistant that answers user questions based only on the supplied context and the article abstract. \
                Only answer using information in the following context and abstract.\
                BEGIN CONTEXT:\
                {context['documents']}\
                END CONTEXT\
                BEGIN ABSTRACT:\
                The HER-2/neu oncogene is a member of the erbB-like \
                oncogene family, and is related to, but distinct from, the \
                epidermal growth factor receptor. This gene has been \
                shown to be amplified in human breast cancer cell lines. \
                In the current study, alterations of the gene in 189 \
                primary human breast cancers were investigated. HER-2/ \
                neu was found to be amplified from 2- to greater than 20- \
                fold in 30% of the tumors. Correlation of gene amplification \
                with several disease parameters was evaluated. Amplification \
                of the HER-2/neu gene was a significant predictor \
                of both overall survival and time to relapse in \
                patients with breast cancer. It retained its significance \
                even when adjustments were made for other known \
                prognostic factors. Moreover, HER-2/neu amplification \
                had greater prognostic value than most currently used \
                prognostic factors, incuding hormonal-receptor status, \
                in lymph node-positive disease. These data indicate that \
                this gene may play a role in the biologic behavior and/or \
                pathogenesis of human breast cancer.\
                END ABSTRACT\
                If the context and abstract don't have the information needed to answer the question, just answer with 'I don't know the answer.' and no other text.\
                Only include your answer and no additional reasoning or thought process."
            }
        ]

    # Add chat history
    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    return generate_completion(message=message, model=model), message
    

def generate_completion(message: List[dict], model: str) -> str:
    """
    Generate the chat completion for the input message

    Args:
        message (List[dict]): Input message with relevant history and/or context
        model (str): The model name to use for completion

    Returns:
        str: Chat completion output message
    """

    client = Client(host='http://host.docker.internal:11434')
    response = client.chat(model=model, messages=message, options={"temperature": 0.0, "top_p": 0.5})

    return response.message.content


def compile_full_response(context: dict, response: str) -> dict:
    """
    Compile the full response with sources

    Args:
        context (dict): The context provided to the LLM when generating the chat completion
        response (str): Chat completion from the LLM

    Returns:
        dict: Dictionary with "sources" (list of the source files, pages, and similarity scores) and LLM response
    """

    sources = []

    for i in range(len(context["ids"][0])):
        filename = (context["metadatas"][0][i]["filename"]).split("/")[-1]
        page = context["metadatas"][0][i]["page_number"]
        score = round(context["distances"][0][i], 3)
        sources.append(f'{filename} page {page}.')
                   

    return {"sources": sources, "response": response}
