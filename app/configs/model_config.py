from .basic_config import OPENAI_API_KEY
LLM_DEVICE = "auto"

MODEL_PRIVIDER = "openai-api"

ONLINE_LLM_MODEL = {
    "openai-api": {
        "model_name": "gpt-3.5-turbo",
        "api_base_url": "https://api.openai.com/v1",
        "api_key": OPENAI_API_KEY,
        "openai_proxy": "",
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
