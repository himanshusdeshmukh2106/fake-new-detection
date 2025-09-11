from .gemini_client import GeminiClient

# fmt: off
CLIENTS = {
    "gemini": GeminiClient,
}
# fmt: on


def model2client(model_name: str):
    """If the client is not specified, use this function to map the model name to the corresponding client."""
    if model_name.startswith("gemini"):
        return GeminiClient
    else:
        raise ValueError(f"Model {model_name} not supported. Only Gemini models are supported.")
