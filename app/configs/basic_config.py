import logging
import os
import langchain
import tempfile
import shutil
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_PRIVIDER = "openai-api"


log_verbose = True
langchain.verbose = False


LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)


ONLINE_LLM_MODEL = {
    "openai-api": {
        "model_name": "gpt-3.5-turbo",
        "api_base_url": "https://api.openai.com/v1",
        "api_key": OPENAI_API_KEY,
        "openai_proxy": "",
        "temperature": 0,
        "max_tokens": None,
    },
    # Azure API
    "azure-api": {
        "deployment_name": "",  # Deploay name
        "resource_name": "",  # https://{resource_name}.openai.azure.com/openai/
        "api_version": "",  # API VERSION
        "api_key": "",
        "provider": "AzureWorker",
    },
}

LLM_MODELS = ["gpt-3.5-turbo"]
TEMPERATURE = 0

PROMPT_TEMPLATES = {
    "llm_chat": {
        "default":
            '{{ input }}',

        "with_history":
            'The following is a friendly conversation between a human and an AI. '
            'The AI is talkative and provides lots of specific details from its context. '
            'If the AI does not know the answer to a question, it truthfully says it does not know.\n\n'
            'Current conversation:\n'
            '{history}\n'
            'Human: {input}\n'
            'AI:',

    },
}