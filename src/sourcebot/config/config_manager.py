# sourcebot/config/config_manager.py
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

from .exceptions import ConfigError
from .global_config import GlobalConfig
from .workspace_config import WorkspaceConfig, ModelConfig
from .provider_config import ProvidersConfig


class ConfigManager:
    """
    Configuration Manager - Separate global configuration and workspace configuration
    """
    
    def __init__(self, app_name: str = "sourcebot"):
        """
        Initialize Configuration Manager

        Args:
            app_name: Application Name
        """
        self.app_name = app_name
        self.app_root_path = Path.home() / f".{app_name}"
        self.global_config_path = self.app_root_path / "config.json"
        self.workspace_config_name = f"{app_name}.workspace.json"
        
        self.app_root_path.mkdir(parents=True, exist_ok=True)
        
        self._global_config: Optional[GlobalConfig] = None
        self._workspace_config: Optional[WorkspaceConfig] = None
        self._current_workspace_path: Optional[Path] = None
    
    # Global Configuration Management
    
    def init_global_config(self, force: bool = False) -> GlobalConfig:
        """
        Initialize global configuration (only once)

        Args:
            force: Whether to force re-initialization

        Returns:
            Global configuration object
        """
        if not force and self.global_config_path.exists():
            return self.load_global_config()
        
        config = GlobalConfig()
        
        self.save_global_config(config)
        print(f"✅ Global configuration has been initialized: {self.global_config_path}")
        
        self._global_config = config
        return config
    
    def load_global_config(self) -> GlobalConfig:
        """
        Load global configuration

        Returns:
            Global configuration object
        """
        if self._global_config is not None:
            return self._global_config
        
        if not self.global_config_path.exists():
            return self.init_global_config()
        
        try:
            with open(self.global_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = GlobalConfig.model_validate(data)
            self._global_config = config
            return config
            
        except Exception as e:
            raise ConfigError(f"Failed to load global configuration: {e}")
    
    def save_global_config(self, config: Optional[GlobalConfig] = None):
        """
        Save global configuration

        Args:
            config: Configuration object; saves cached configuration when None is selected.
        """
        config = config or self._global_config
        if config is None:
            raise ConfigError("No global configuration can be saved")
        
        config.update_timestamp()
        
        try:
            self.global_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(exclude_none=True), f, indent=2, ensure_ascii=False)
            
            self._global_config = config
            print(f"✅ Global configuration has been saved")
            
        except Exception as e:
            raise ConfigError(f"Failed to save global configuration: {e}")
    
    # Provider Configuration Management
    
    def set_provider_config(self, provider: str, api_key: str, api_base: Optional[str] = None, **kwargs):
        """
        Configure Provider

        Args:
            Provider: Provider name
            API_key: API key
            API_base: API base URL
            **Kwargs: Other configurations
        """
        global_config = self.load_global_config()
        
        provider_config = getattr(global_config.providers, provider, None)
        if provider_config is None:
            raise ConfigError(f"Unsupported providers: {provider}")
        
        provider_config.api_key = api_key
        if api_base:
            provider_config.api_base = api_base
        for key, value in kwargs.items():
            if hasattr(provider_config, key):
                setattr(provider_config, key, value)
        
        self.save_global_config(global_config)
        print(f"✅ {provider} configuration has been updated")
    
    def get_provider_config(self, provider: str):
        """Get provider configuration"""
        global_config = self.load_global_config()
        return getattr(global_config.providers, provider, None)
    
    def list_providers(self, only_configured: bool = False) -> Dict[str, Any]:
        """List all providers"""
        global_config = self.load_global_config()
        
        if only_configured:
            return {name: config for name, config in global_config.providers if config.is_configured()}
        else:
            return {name: config for name, config in global_config.providers}
    
    # Workspace Configuration Management
    
    def find_workspace_config(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Locate workspace configuration file

        Args:
            start_path: Starting path

        Returns:
            Configuration file path
        """
        if start_path is None:
            start_path = Path.cwd()
        
        start_path = start_path.absolute()
        
        current = start_path
        while current != current.parent:
            config_file = current / self.workspace_config_name
            if config_file.exists():
                return config_file
            current = current.parent
        
        return None
    
    def load_workspace_config(self, workspace_path: Optional[Path] = None) -> Optional[WorkspaceConfig]:
        """
        Load workspace configuration

        Args:
            workspace_path: Workspace path
        Returns:
            Workspace configuration object; returns None if not found.
        """
        config_path = self.find_workspace_config(workspace_path)
        if not config_path:
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = WorkspaceConfig.model_validate(data)
            self._workspace_config = config
            self._current_workspace_path = config_path.parent
            return config
            
        except Exception as e:
            raise ConfigError(f"Failed to load workspace configuration: {e}")
    
    def init_workspace_config(self, project_name: str, project_path: Optional[Path] = None,
                              default_model: Optional[str] = None) -> WorkspaceConfig:
        """
        Initialize workspace configuration

        Args:
            project_name: Project name
            project_path: Project path
            default_model: Default model name
        Returns:
            Workspace configuration object
        """
        if project_path is None:
            project_path = Path.cwd()
        else:
            project_path = Path(project_path).expanduser().resolve()
        
        project_path.mkdir(parents=True, exist_ok=True)
        config_path = project_path / self.workspace_config_name
        if config_path.exists():
            response = input(f"The workspace configuration already exists: {config_path}\nShould it be overwritten? (y/N): ")
            if response.lower() != 'y':
                return self.load_workspace_config(project_path)
        
        config = WorkspaceConfig(
            project_name=project_name,
            project_root=str(project_path)
        )
        
        if default_model:
            global_config = self.load_global_config()
            config.add_model(
                name="default",
                provider=global_config.default_provider,
                model=default_model
            )
            config.default_model = "default"
        
        self.save_workspace_config(config, project_path)
        
        self._workspace_config = config
        self._current_workspace_path = project_path
        
        return config
    
    def save_workspace_config(self, config: WorkspaceConfig, project_path: Optional[Path] = None):
        """
        Save workspace configuration
        Args:
            config: Workspace configuration
            project_path: Project path
        """
        if project_path is None:
            project_path = Path(config.project_root)
        else:
            project_path = Path(project_path).expanduser().resolve()
        
        project_path.mkdir(parents=True, exist_ok=True)
        
        config_path = project_path / self.workspace_config_name
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(exclude_none=True), f, indent=2, ensure_ascii=False)
            
            print(f"✅ Workspace configuration has been saved: {config_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to save workspace configuration: {e}")
    
    # Model Configuration Management
    
    def add_model_to_workspace(self, name: str, provider: str, model: str,
                               workspace_path: Optional[Path] = None, **kwargs):
        """
        Add a model to the workspace configuration

        Args:
            name: Model name
            provider: Provider name
            model: Model name
            workspace_path: Workspace path
            **kwargs: Other model parameters
        """
        global_config = self.load_global_config()
        provider_config = getattr(global_config.providers, provider, None)
        if not provider_config or not provider_config.is_configured():
            print(f"Warning: Provider {provider} has not set the API key in the global configuration.")
        
        workspace_config = self.load_workspace_config(workspace_path)
        if not workspace_config:
            if workspace_path is None:
                workspace_path = Path.cwd()
            workspace_config = self.init_workspace_config(
                project_name=workspace_path.name,
                project_path=workspace_path
            )
        
        workspace_config.add_model(name, provider, model, **kwargs)
        
        if workspace_config.default_model == "default" and name != "default":
            workspace_config.default_model = name
        
        self.save_workspace_config(workspace_config)
        print(f"✅ The model {name} ({provider}/{model}) has been added to the workspace.") 
        
    
    def get_model_for_workspace(self, model_name: Optional[str] = None,
                                workspace_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Retrieves the workspace model configuration (including the global API key)
        Args:
            model_name: Model name; default model is used if None
            workspace_path: Workspace path
        Returns:
            A dictionary containing the complete configuration (model parameters + API key, etc.)
        """

        workspace_config = self.load_workspace_config(workspace_path)
        if not workspace_config:
            raise ConfigError("Workspace configuration not found, please initialize first.")
        
        model_config = workspace_config.get_model_config(model_name)
        if not model_config:
            raise ConfigError(f"The model does not exist: {model_name or workspace_config.default_model}")
        
        global_config = self.load_global_config()
        provider_config = global_config.get_provider_config(model_config.provider)
        
        if not provider_config or not provider_config.is_configured():
            raise ConfigError(f"The provider {model_config.provider} does not have an API key configured.")
        
        result = {
            "provider": model_config.provider,
            "model": model_config.model,
            "api_key": provider_config.api_key,
            "api_base": provider_config.api_base,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "top_p": model_config.top_p,
        }
        
        if provider_config.extra_headers:
            result["extra_headers"] = provider_config.extra_headers
        
        return result
    
    # Tools and Methods
    
    @property
    def current_workspace(self) -> Optional[WorkspaceConfig]:
        """Get current workspace configuration"""
        if self._workspace_config is None:
            self._workspace_config = self.load_workspace_config()
        return self._workspace_config
    
    @property
    def in_workspace(self) -> bool:
        return self.current_workspace is not None
    
    def get_workspace_path(self) -> Optional[Path]:
        """Get the current workspace path"""
        if self._current_workspace_path:
            return self._current_workspace_path
        config_path = self.find_workspace_config()
        return config_path.parent if config_path else None