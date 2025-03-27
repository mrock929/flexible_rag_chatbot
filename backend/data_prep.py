# File to handle all data ingestion, chunking, embedding, and storage

import glob
from typing import List, Tuple
from pathlib import Path
import os

import chromadb
from PyPDF2 import PdfReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from dotenv import load_dotenv
from openai import OpenAI

INPUT_DATA_PATH = ".\data\*.pdf"
DB_PATH = "./data/chromadb/"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 20


def prepare_data() -> Tuple[chromadb.Collection, OpenAI]:
    """
    Data preparation pipeline. Ingests documents, chunks them, and embeds them in a ChromaDB vectorstore.

    Returns:
        Tuple[chromadb.Collection, OpenAI]: Tuple with the ChromaDB collection with the input document chunked and embedded and the OpenAI client
    """

    openai_client = openai_setup()
    file_text, filenames = read_data()
    print("Files read")
    documents = chunk_data(docs=file_text, doc_names=filenames)
    print("Data chunked")
    collection = manage_db()
    print("db setup")
    upsert_db(collection=collection, data=documents)
    print("data added to db")
    
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

    files = glob.glob(INPUT_DATA_PATH)
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


def chunk_data(docs: List[List[str]], doc_names: List[str]) -> List[Document]:
    """
    For all documents, break each page into smaller chunks for retrieval and embedding.

    Args:
        docs (List[List[str]]): List of document text. Each document has a list of text, one entry per page.
        doc_names (List[str]): List of document filenames

    Returns:
        List[Document]: List of llamaindex Document objects ctonaining text, metadata (filename, page_number, chunk_number), and doc_id
    """

    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # For each page of text, chunk it based on below, maintain page number
    documents = []
    for i, doc in enumerate(docs):
        for j, page in enumerate(doc):
            page_text = splitter.split_text(text=page)
            for k, chunk in enumerate(page_text):
                documents.append(
                    Document(
                        text=chunk,
                        metadata={
                            "filename": doc_names[i],
                            "page_number": j + 1,
                            "chunk_number": k,
                        },
                        doc_id=f"{doc_names[i]}_page{j}_chunk{k}",
                    )
                )

    return documents


def manage_db() -> chromadb.Collection:
    """
    Create the persistent chroma db and set up the vectorstore.

    Returns:
        chromadb.Collection: Persistent ChromaDB collection (vector db/vectorstore)
    """
    chroma_client = chromadb.PersistentClient(path=DB_PATH)

    # Create a collection if it doesn't already exist, default embedding model is Sentence Transformer (SBERT)
    collection = chroma_client.get_or_create_collection(
        name="docs", metadata={"hnsw:space": "cosine"}
    )

    return collection


def upsert_db(collection, data: List[Document]) -> None:

    # switch `add` to `upsert` to avoid adding the same documents every time
    # TODO just send in the list, likely don't use Document or construct differently so more efficient
    for doc in data:
        collection.upsert(documents=doc.text, metadatas=doc.metadata, ids=doc.doc_id)
