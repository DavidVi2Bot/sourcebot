# sourcebot/llm/anthropic/anthropic_llm_client.py
from sourcebot.config import ConfigManager
from anthropic import AsyncAnthropic
from sourcebot.llm.core.client import BaseLLMClient
from .adapter import AnthropicAdapter
from sourcebot.llm.anthropic.converter import to_anthropic_messages, to_anthropic_tools
from sourcebot.llm.core.tool_converter import normalize_tools

class AnthropicLLMClient(BaseLLMClient):

    def __init__(self, config_manager, provider_name: str = "anthropic", model_name: str = "claude-3-opus-20240229"):
        provider_config = config_manager.get_provider_config(provider_name)
        self.client = AsyncAnthropic(
            api_key = provider_config.api_key,
            base_url = provider_config.api_base
        )
        self.temperature = provider_config.temperature
        self.model_name = model_name
        self.adapter = AnthropicAdapter()

    async def complete(self, messages, tools = None):
        tools = normalize_tools(tools)
        system, amsgs = to_anthropic_messages(messages)
        req = {
            "model": self.model_name,
            "messages": amsgs,
            "max_tokens": 4096,
        }
        
        if system:
            req["system"] = system

        if tools:
            req["tools"] = to_anthropic_tools(tools)

        resp = await self.client.messages.create(**req)

        return self.adapter.from_response(resp)