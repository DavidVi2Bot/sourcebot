# sourcebot/cli/commands/init_global_config.py 
from sourcebot.config import ConfigManager
from rich.console import Console
from rich.prompt import Confirm
console = Console()

def init_global_config():


    config_manager = ConfigManager()
    global_config_path = config_manager.global_config_path
  

    if global_config_path.exists():
        

        console.print(f"[yellow]Config already exists at {global_config_path}[/yellow]")
        console.print("  [bold]y[/bold] = overwrite with defaults (existing values will be lost)")
        console.print("  [bold]N[/bold] = refresh config, keeping existing values and adding new fields")

        confirm = Confirm.ask("[bold]Execute?[/bold]", default=True)

        if confirm:
            config_manager.init_global_config(True)
            console.print(f"[green]✓[/green] Config reset to defaults at {global_config_path}")
        else:
            console.print(f"[green]✓[/green] Config refreshed at {global_config_path} (existing values preserved)")
    else:
        config_manager.init_global_config()
        console.print(f"[green]✓[/green] Created config at {global_config_path}")
