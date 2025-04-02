# File to create and manage a database that tracks all user queries, responses, and feedback for continuous model improvement

import json
import sqlite3
from typing import List


def manage_tracking_db() -> sqlite3.Connection:
    """Connect to the chatbot_data database. Create it if it doesn't exist.
    Creates the chatbot table. Primary key is (query_timestamp, user_query)"""

    con = sqlite3.connect(
        "/app/data/chatbot_data.db", check_same_thread=False
    )  # Only one execute at a time will be run, so check_same_thread=False is safe
    cursor = con.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS chatbot(query_timestamp, user_query, retrieval_query, full_query, llm_response, sources, is_good)"
    )

    return con


def add_tracking_entry(
    connection: sqlite3.Connection,
    query_timestamp: str,
    user_query: str,
    retrieval_query: str,
    full_query: str,
    llm_response: str,
    sources: List[str],
) -> None:
    """
    Add an entry to the chatbot data tracking database. Primary key is (query_timestamp, user_query)

    Args:
        connection (sqlite3.Connection): Valid sqlite3 connection for the database
        query_timestamp (str): The timestamp of the query as a string
        user_query (str): The original user query as typed into the chatbot
        retrieval_query (str): The LLM-modified user query used to retrieve information from the vectorstore with sources material embedded and chunked
        full_query (str): The full query sent to the LLM, contains the user query and the context
        llm_response (str): The response generated by the LLM
        sources (List[str]): The list of sources (filename and page number in a string) in the context
    """

    cursor = connection.cursor()

    # is_good is the final column. This is NULL until the user clicks the UI button that designates this response as good or bad
    cursor.execute(
        """INSERT INTO chatbot (query_timestamp, user_query, retrieval_query, full_query, llm_response, sources) VALUES (?, ?, ?, ?, ?, ?)""",
        (
            query_timestamp,
            user_query,
            retrieval_query,
            json.dumps(full_query),
            llm_response,
            json.dumps(sources),
        ),
    )
    connection.commit()


def update_entry_with_feedback(connection: sqlite3.Connection, is_good: bool) -> None:
    """
    Update the most recent entry in the chatbot data tracking database with user feedback (is_good column, true or false)

    Args:
        connection (sqlite3.Connection): Valid sqlite3 connection for the database
        is_good (bool): True if the LLM response was good, False if it was not
    """
    cursor = connection.cursor()

    # Assume we're using the most recent entry
    output = cursor.execute(
        """SELECT query_timestamp, user_query FROM chatbot WHERE query_timestamp == (SELECT MAX(query_timestamp) FROM chatbot)"""
    )
    row = output.fetchone()
    query_timestamp = row[0]
    user_query = row[1]

    cursor.execute(
        """UPDATE chatbot SET is_good = ? WHERE query_timestamp = ? AND user_query = ?""",
        (is_good, query_timestamp, user_query),
    )
    connection.commit()
