# sourcebot/llm/core/adapter.py

from abc import ABC, abstractmethod
from .response import LLMResponse
from .delta import LLMDelta


class BaseAdapter(ABC):

    @abstractmethod
    def from_response(self, response) -> LLMResponse:
        pass

    def stream_chunk(self, chunk) -> LLMDelta:
        """Optional: Streaming parsing"""
        return LLMDelta()