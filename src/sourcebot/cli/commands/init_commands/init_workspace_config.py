from sourcebot.config import ConfigManager
from rich.console import Console
from pathlib import Path

def init_workspace_config():
    console = Console()
    config_manager = ConfigManager()
    project_path = Path.cwd()
    project_name = project_path.name
    
    if config_manager.load_workspace_config():
        current_configuration = config_manager.find_workspace_config()
        console.print(f"[yellow]Workspace config already exists at {current_configuration}[/yellow]")
    else: 
        config_manager.init_workspace_config(
            project_name = project_name,
            project_path = project_path
        )
