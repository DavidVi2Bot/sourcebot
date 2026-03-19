# sourcebot/cli/commands/core/command_line.py
from sourcebot.cli.commands.run_commands import CommandLineTool
from sourcebot.runtime import InitSystem
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


async def command_line():
    
    init_system = InitSystem()
    console = init_system.console

    command_line_tool = CommandLineTool(
        console = console,
        docker_sandbox = init_system.docker_sandbox,
        dag_planner = init_system.dag_planner,
        dag_scheduler = init_system.dag_scheduler,
        conversation_service = init_system.conversation_service
    )
    try:
        from sourcebot.cli.commands.run_commands import SafeRunner
        runner = SafeRunner(command_line_tool)
        await runner.run()
    except EOFError:
        console.print("\nGoodbye!")
