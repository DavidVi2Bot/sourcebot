# sourcebot/config/workspace_config.py
from pathlib import Path
from pydantic import Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import Base


class ModelConfig(Base):
    """Model configuration"""
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p")
    
    @field_validator('provider')
    def validate_provider(cls, v):
        """Validate provider name"""
        # Only basic validation here, specific availability is determined by global configuration
        if not v or not isinstance(v, str):
            raise ValueError("Provider name must be a non-empty string")
        return v.lower()


class WorkspaceConfig(Base):
    """Workspace configuration - saved independently for each project"""
    
    # Project information
    project_name: str = Field(..., description="Project name")
    project_root: str = Field(..., description="Project root directory")
    project_rules: str = Field("", description="Project rules keywords")
    project_skill: str = Field("", description="Project skill keywords")
    docker_image: str = Field("python:3.11-slim", description="docker image")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation time")
    
    # Model configuration
    models: Dict[str, ModelConfig] = Field(
        default_factory=lambda: {
        "main_agent": ModelConfig(
            provider = "dashscope",
            model = "qwen3.5-plus",
            temperature = 0.7,
            max_tokens = 2000,  
            top_p = 1.0
        ),
        "sub_agent": ModelConfig(
            provider = "dashscope",
            model = "qwen3.5-plus",
            temperature = 0.7,
            max_tokens = 2000,
            top_p = 1.0
        )
        },

    )
    
    # Workspace settings
    context_files: List[str] = Field(default_factory=list, description="Context file patterns")
    ignore_patterns: List[str] = Field(
        default_factory=lambda: ["**/__pycache__", "**/.git", "**/.idea", "**/*.pyc"],
        description="Ignore file patterns"
    )
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Maximum file size (bytes)")
    
    # Custom settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    def get_model_config(self, model_name: Optional[str] = None) -> Optional[ModelConfig]:
        """Get model configuration"""
        if model_name is None:
            model_name = self.default_model
        return self.models.get(model_name)
    
    def add_model(self, name: str, provider: str, model: str, **kwargs):
        """Add model configuration"""
        self.models[name] = ModelConfig(provider=provider, model=model, **kwargs)
    
    @property
    def root_path(self) -> Path:
        """Get project root directory path"""
        return Path(self.project_root).expanduser().resolve()
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "my-ai-project",
                "project_root": "/home/user/projects/my-ai-project",
                "project_rules": "python", 
                "project_skill": "python",
                "docker_image": "python:3.11-slim",
                "models": {
                    "gpt4": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "temperature": 0.7
                    },
                    "claude": { # TODO: Anthropic compatible
                        "provider": "anthropic",
                        "model": "claude-3-opus-20240229",
                        "temperature": 0.5
                    }
                }
            }
        }