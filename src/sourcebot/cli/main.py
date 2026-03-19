# src/sourcebot/cli/main.py
import typer
import sys

app = typer.Typer(
    name = "sourcebot",
    no_args_is_help = True,
    add_completion = False
)
@app.command("init")
def init():
    """Init global config"""
    from sourcebot.cli.commands.init_commands import init_global_config
    init_global_config()
@app.command("init_workspace")  
def agent():
    """Init workspace config"""
    from sourcebot.cli.commands.init_commands import init_workspace_config
    init_workspace_config()
@app.command("cli")  
def test_init_agent_system():
    """Start SourceBot AI Assistant CLI"""
    from sourcebot.cli.commands.run_commands import SafeRunner
    from sourcebot.cli.commands.core import command_line
    import asyncio
    runner = SafeRunner(command_line)
    asyncio.run(runner.run())

