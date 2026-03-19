# src/sourcebot/config/provider_config.py
from pydantic import Field
from typing import Optional, Dict
from .base import Base


class ProviderConfig(Base):
    """LLM provider configuration."""
    
    api_key: str = Field(default="", description="API key")
    api_base: str = Field(default="", description="API base URL")
    temperature: float = 0.7
    extra_headers: Optional[Dict[str, str]] = Field(default=None, description="Custom request headers")
    timeout: Optional[int] = Field(default=None, description="Timeout (seconds)")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    
    def is_configured(self) -> bool:
        """Check if it is configured"""
        return bool(self.api_key)


class ProvidersConfig(Base):
    """Configuration for LLM providers."""
    
    custom: ProviderConfig = Field(default_factory=ProviderConfig, description="Custom OpenAI compatible endpoints")
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig, description="Anthropic Claude")
    openai: ProviderConfig = Field(default_factory=ProviderConfig, description="OpenAI")
    openrouter: ProviderConfig = Field(default_factory=ProviderConfig, description="OpenRouter")
    

    deepseek: ProviderConfig = Field(default_factory=ProviderConfig, description="DeepSeek")
    zhipu: ProviderConfig = Field(default_factory=ProviderConfig, description="zhipu")
    dashscope: ProviderConfig = Field(default_factory=ProviderConfig, description="dashscope")
    moonshot: ProviderConfig = Field(default_factory=ProviderConfig, description="Moonshot AI")
    minimax: ProviderConfig = Field(default_factory=ProviderConfig, description="MiniMax")
    
    aihubmix: ProviderConfig = Field(default_factory=ProviderConfig, description="AiHubMix API gateway")
    siliconflow: ProviderConfig = Field(default_factory=ProviderConfig, description="SiliconFlow")
    volcengine: ProviderConfig = Field(default_factory=ProviderConfig, description="volcengine")
    
 
    groq: ProviderConfig = Field(default_factory=ProviderConfig, description="Groq")
    vllm: ProviderConfig = Field(default_factory=ProviderConfig, description="vLLM")
    gemini: ProviderConfig = Field(default_factory=ProviderConfig, description="Google Gemini")
    
    # OAuth
    openai_codex: ProviderConfig = Field(default_factory=ProviderConfig, description="OpenAI Codex (OAuth)")
    github_copilot: ProviderConfig = Field(default_factory=ProviderConfig, description="Github Copilot (OAuth)")
    
    def get_provider(self, name: str) -> ProviderConfig:
        """Retrieve provider configuration for a specified name"""
        return getattr(self, name, None)
    
    def list_configured(self) -> list[str]:
        """List all configured providers"""
        return [name for name, provider in self if provider.is_configured()]
    
    def __iter__(self):
        """Iterate through all providers"""
        for field_name in self.model_fields:
            if field_name not in ['model_config']:
                yield field_name, getattr(self, field_name)