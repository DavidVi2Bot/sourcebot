# sourcebot/llm/core/client.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from .response import LLMResponse
from .delta import LLMDelta


class BaseLLMClient(ABC):

    @abstractmethod
    async def complete(self, messages, tools = None) -> LLMResponse:
        pass

    async def stream(self, messages, tools = None) -> AsyncGenerator[LLMDelta, None]:
        raise NotImplementedError