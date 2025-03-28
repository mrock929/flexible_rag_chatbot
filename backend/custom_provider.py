from typing import Dict, Any

#from promptfoo.src.types import ProviderResponse

from chatbot import query_chatbot
from data_prep import prepare_data

def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> dict: #ProviderResponse:
    # Note: The prompt may be in JSON format, so you might need to parse it.
    # For example, if the prompt is a JSON string representing a conversation:
    # prompt = '[{"role": "user", "content": "Hello, world!"}]'
    # You would parse it like this:
    # prompt = json.loads(prompt)

    # The 'options' parameter contains additional configuration for the API call.
    # config = options.get('config', None)
    # additional_option = config.get('additionalOption', None)

    # # The 'context' parameter provides info about which vars were used to create the final prompt.
    # user_variable = context['vars'].get('userVariable', None)

    # The prompt is the final prompt string after the variables have been processed.
    # Custom logic to process the prompt goes here.
    # For instance, you might call an external API or run some computations.
    index, openai_client = prepare_data()
    
    response = query_chatbot(query=prompt, index=index, openai_client=openai_client, history=[{"role": "user", "content": prompt}])

    # The result should be a dictionary with at least an 'output' field.
    result = {
        "output": response["response"],
    }

    # if some_error_condition:
    #     result['error'] = "An error occurred during processing"

    # if token_usage_calculated:
    #     # If you want to report token usage, you can set the 'tokenUsage' field.
    #     result['tokenUsage'] = {"total": token_count, "prompt": prompt_token_count, "completion": completion_token_count}

    # if failed_guardrails:
    #     # If guardrails triggered, you can set the 'guardrails' field.
    #     result['guardrails'] = {"flagged": True}

    return result

# def call_embedding_api(prompt: str) -> ProviderEmbeddingResponse:
#     # Returns ProviderEmbeddingResponse
#     pass

# def call_classification_api(prompt: str) -> ProviderClassificationResponse:
#     # Returns ProviderClassificationResponse
#     pass