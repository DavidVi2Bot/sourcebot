# sourcebot/config/global_config.py
from pathlib import Path
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime

from .base import Base
from .provider_config import ProvidersConfig


class GlobalConfig(Base):
    """Global configuration - initialized only once, saved in ~/.sourcebot/config.json"""
    
    version: str = Field(default="1.0.0", description="Configuration version")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation time")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Update time")
    
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig, description="LLM provider configuration")
    
    default_provider: str = Field(default="dashscope", description="Default provider")
    default_model: str = Field(default="qwen3.5-plus", description="Default model")
    
    cache_dir: str = Field(default=str(Path.home() / ".cache" / "sourcebot"), description="Cache directory")
    log_level: str = Field(default="info", description="Log levels")
    
    def update_timestamp(self):
        """Update timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def get_provider_config(self, provider_name: str) -> Optional[Any]:
        """Get the configuration of the specified provider"""
        return getattr(self.providers, provider_name, None)
    
    def is_provider_configured(self, provider_name: str) -> bool:
        """Check if the provider has been configured"""
        provider = self.get_provider_config(provider_name)
        return provider is not None and provider.is_configured()
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0.0",
                "default_provider": "openai",
                "default_model": "gpt-4",
                "providers": {
                    "openai": {
                        "api_key": "sk-...",
                        "api_base": "https://api.openai.com/v1"
                    },
                    "anthropic": {
                        "api_key": "sk-ant-..."
                    }
                }
            }
        }