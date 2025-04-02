# This file allows promptfoo to properly use the locally downloaded model for testing

from typing import Dict, Any

from chatbot import query_chatbot
from data_prep import prepare_data

LOCAL_TESTING_MODEL = "llama3.2"  # Change this model name to whichever model you want to test, the name should match the named used in the ollama pull command


def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> dict:
    """
    Functional call used by promptfoo to properly call the chatbot using the LOCAL_TESTING_MODEL

    Args:
        prompt (str): Test case input prompt
        options (Dict[str, Any]): Test case options (unused)
        context (Dict[str, Any]): Test case context (unused)

    Returns:
        dict: Model response
    """

    index = prepare_data()

    response = query_chatbot(
        query=prompt,
        index=index,
        model=LOCAL_TESTING_MODEL,
        history=[{"role": "user", "content": prompt}],
        connection=None,
        is_test=True,
    )

    # The result should be a dictionary with at least an 'output' field.
    result = {
        "output": response["response"],
    }

    return result
