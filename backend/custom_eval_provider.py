# This file allows promptfoo to evaluate model outputs with the locally downloaded model

from typing import Dict, Any

from chatbot import generate_completion

LOCAL_EVAL_MODEL = "gemma3:27b"  # Not recommended to go below 14B parameters

def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> dict: 
    """
    Functional call used by promptfoo to properly call the evaluation model using the LOCAL_EVAL_MODEL

    Args:
        prompt (str): Test case input prompt
        options (Dict[str, Any]): Test case options (unused)
        context (Dict[str, Any]): Test case context (unused)

    Returns:
        dict: Model response
    """
    
    response = generate_completion(message=[{"role": "user", "content": prompt}], model=LOCAL_EVAL_MODEL)

    # The result should be a dictionary with at least an 'output' field.
    result = {
        "output": response,
    }

    return result
