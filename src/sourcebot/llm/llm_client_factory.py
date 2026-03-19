# sourcebot/llm/llm_client_factory.py
from sourcebot.llm.openai import OpenAILLMClient
from sourcebot.llm.anthropic import AnthropicLLMClient

class LLMClientFactory:
    @staticmethod
    def create_client(config_manager, provider_name: str, model_name: str = None):
        """Create the corresponding client based on the provider."""

        if provider_name in ["anthropic", "claude"]:
            return AnthropicLLMClient(config_manager, provider_name, model_name)
        else:
            return OpenAILLMClient(config_manager, provider_name, model_name)