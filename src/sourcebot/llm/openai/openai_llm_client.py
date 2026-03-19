# sourcebot/llm/openai/openai_llm_client.py
from openai import AsyncOpenAI
from sourcebot.llm.core.client import BaseLLMClient
from .adapter import OpenAIAdapter
from sourcebot.config import ConfigManager
from sourcebot.llm.openai.converter import to_openai_messages, to_openai_tools
from sourcebot.llm.core.tool_converter import normalize_tools
class OpenAILLMClient(BaseLLMClient):

    def __init__(self, config_manager, provider_name: str = "dashscope", model_name: str = "qwen3.5-plus"):
        provider_config = config_manager.get_provider_config(provider_name)
        self.client = AsyncOpenAI(
            api_key = provider_config.api_key,
            base_url = provider_config.api_base
        )
        self.temperature = provider_config.temperature
        self.model = model_name
        self.adapter = OpenAIAdapter()

    async def complete(self, messages, tools = None):
        # messages = normalize_messages(messages)
        oai_msgs = to_openai_messages(messages)
        tools = normalize_tools(tools)
        oai_tools = to_openai_tools(tools) if tools else None
        resp = await self.client.chat.completions.create(
            model = self.model,
            messages = oai_msgs,
            temperature = self.temperature,
            tools = oai_tools,
        )
        return self.adapter.from_response(resp)

    async def stream(self, messages, tools=None):
        stream = await self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            tools = tools,
            stream = True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta

            yield {
                "content": delta.content or "",
                "tool_calls": delta.tool_calls,
            }