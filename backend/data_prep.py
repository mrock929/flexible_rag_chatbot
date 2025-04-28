# File to handle all data ingestion, chunking, embedding, and storage

import glob
from typing import List, Tuple
from pathlib import Path
import os

import chromadb
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
import semchunk
from transformers import AutoTokenizer

CHUNK_SIZE = 500
CHUNK_OVERLAP = 20


def prepare_data() -> Tuple[chromadb.Collection, OpenAI]:
    """
    Data preparation pipeline. Ingests documents, chunks them, and embeds them in a ChromaDB vectorstore.

    Returns:
        Tuple[chromadb.Collection, OpenAI]: Tuple with the ChromaDB collection with the input document chunked and embedded and the OpenAI client
    """

    openai_client = openai_setup()

    if not os.path.isfile('./data/chromadb/chroma.sqlite3'):
        # Only read and chunk data if the DB doesn't exist
        file_text, filenames = read_data()
        print("Files read")
        chunk_list, metadata_list, id_list = chunk_data(docs=file_text, doc_names=filenames)
        print("Data chunked")
        collection = manage_db()
        print("db set up")
        insert_data_to_db(collection=collection, chunk_list=chunk_list, metadata_list=metadata_list, id_list=id_list)
        print("data added to db")
    else:
        collection = manage_db()
        print("db set up")

    return collection, openai_client


def openai_setup() -> OpenAI:
    """
    Load the OpenAI API Key from the .env file and sets the OpenAI client
    """
    load_dotenv(Path("./.env"))
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    return client


def read_data() -> Tuple[List[List[str]], List[str]]:
    """
    Read all data from the input data directory and extract the raw text.

    Returns:
        Tuple[List[List[str]], List[str]]: Tuple with the list of raw text per document (one entry per page), and a list of the filenames.
    """

    files = glob.glob("./data/*.pdf")
    extracted_files = []
    extracted_filenames = []
    for file in files:
        file_text = []
        reader = PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            file_text.append(page_text)
        extracted_files.append(file_text)
        extracted_filenames.append(file)
        print(f"{len(reader.pages)} pages read from {file}.\n")

    return extracted_files, extracted_filenames


def chunk_data(docs: List[List[str]], doc_names: List[str]) -> Tuple[List[str], List[dict], List[str]]:
    """
    For all documents, break each page into smaller chunks for retrieval and embedding.

    Args:
        docs (List[List[str]]): List of document text. Each document has a list of text, one entry per page.
        doc_names (List[str]): List of document filenames

    Returns:
        Tuple[List[str], List[dict], List[str]]: List of text chunks, the associated metadata (filename, page_number, chunk_number), and doc id
    """

    chunker = semchunk.chunkerify(tokenizer_or_token_counter=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"), chunk_size=CHUNK_SIZE)

    chunk_text = []
    chunk_metadata = []
    chunk_ids = []
    for i, doc in enumerate(docs):
        for j, page in enumerate(doc):
            chunks = chunker(text_or_texts=page, overlap=CHUNK_OVERLAP)
            for k, chunk in enumerate(chunks):
                chunk_text.append(chunk)
                chunk_metadata.append({"filename": doc_names[i], "page_number": j + 1, "chunk_number": k})
                chunk_ids.append(f"{doc_names[i]}_page{j}_chunk{k}")

    return chunk_text, chunk_metadata, chunk_ids


def manage_db() -> chromadb.Collection:
    """
    Create the persistent chroma db and set up the vectorstore. If the collection already exists, connect to it.

    Returns:
        chromadb.Collection: Persistent ChromaDB collection (vectorstore)
    """
    chroma_client = chromadb.PersistentClient(path="./data/chromadb/")

    # Create a collection if it doesn't already exist, default embedding model is sentence-transformers/all-MiniLM-L6-v2
    collection = chroma_client.get_or_create_collection(
        name="docs", metadata={"hnsw:space": "ip"}
    )

    return collection


def insert_data_to_db(collection: chromadb.Collection, chunk_list: List[str], metadata_list: List[dict], id_list: List[str]) -> None:
    """
    Embed and add all chunks of data to the ChromaDB

    Args:
        collection (chromadb.Collection): The ChromaDB collection set up in manage_db()
        chunk_list (List[str]): List of text chunks
        metadata_list (List[dict]): List of metadata (filename, page_number, chunk_number) for each chunk
        id_list (List[str]): List of ids for each chunk
    """

    collection.add(documents=chunk_list, metadatas=metadata_list, ids=id_list)


def get_available_models() -> List[str]:
    """
    Determines the available local models to run in the app that were previously pulled in Ollama.

    Returns:
        List[str]: List of all model names
    """
    model_list = ["gpt-4o-mini"]

    model_paths = glob.glob("./models/manifests/registry.ollama.ai/library/*")
    for model in model_paths:
        model_list.append(model.split("/")[-1])

    return model_list