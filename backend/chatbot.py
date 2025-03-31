# File to create OpenAI chatbot responses based on user queries

from typing import List

from chromadb import Collection
from ollama import Client

NUM_RESULTS = 5
MAX_HISTORY = 4  # Sets the number of previous messages to include in the history


def query_chatbot(query: str, index: Collection, model: str, history: List[dict]) -> dict:
    """
    Retrieves context based on the user query and then generates a response.

    Args:
        query (str): User query from the frontend
        index (Collection): Chunked and embedded text to retrieve from
        model (str): The selected LLM to use for generating the response
        history (List[dict]): History of the chat session

    Returns:
        dict: The response to the user's query from the model. Dictionary with "response" (str) and "sources" (List[str]).
    """
    full_query = update_query(query=query, model=model, history=history)
    print(f"query={query}\nfull query={full_query}\n")
    context = retrieve_context(query=full_query, index=index)
    response = generate_response(context=context, model=model, history=history)
    chat_output = compile_full_response(context=context, response=response)

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
                    Only return the updated user query and no additional text or explanation.\
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
                    END ARTICLE ABSTRACT"
            }
        ]

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


def generate_response(context: dict, model: str, history: List[dict]) -> str:
    """
    Generate the response to the user query based on the supplied context, history, and user query.

    Args:
        context (dict): Retrieved context from source documents
        model (str): The LLM to use to generate the response
        history (List[dict]): Chat history, including the user query

    Returns:
        str: The Gen AI generated response to the user query
    """

    message = [
            {
                "role": "system",
                "content": f"You are an assistant that answers user questions based only on the supplied context and the article abstract. \
                Only answer using information in the supplied context and abstract.\
                If the context and abstract don't have the information needed to answer the question, just answer with 'I don't know the answer.'.\
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
                END ABSTRACT"
            }
        ]

    for m in history[-MAX_HISTORY-1:]:
        message.append({"role": m["role"], "content": m["content"]})

    return generate_completion(message=message, model=model)
    

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
    response = client.chat(model=model, messages=message)

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
