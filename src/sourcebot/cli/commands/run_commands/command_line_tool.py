# sourcebot/cli/commands/command_line_tool.py
import asyncio
import shlex
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich import print as rprint
from rich.markdown import Markdown
import cmd2
from sourcebot.bus import InboundMessage
from sourcebot import __name__
class CommandType(Enum):
    SHELL = "shell"       # Shell commands
    PYTHON = "python"     # Python code execution
    SYSTEM = "system"     # System commands

@dataclass
class Command:
    """Command data class"""
    type: CommandType
    name: str
    content: str
    args: Optional[Dict[str, Any]] = None
    
class CommandLineTool:
    """Command line branching tool main class"""
    
    def __init__(
        self,
        console,
        docker_sandbox,
        dag_scheduler,
        dag_planner,
        conversation_service  
        ):
        self.console = console
        self.docker_sandbox = docker_sandbox
        self.dag_planner = dag_planner  
        self.dag_scheduler = dag_scheduler
        
        self.command_history = []
        self.last_plan_tasks = None  # Store recently generated plans
        self.conversation_service = conversation_service
        self._running = True

    async def run(self):
        try:
            await self._startup()
            await self._loop()
        except Exception as e:
            self.console.print(f"[red]Fatal: {e}[/red]")
        finally:
            await self._shutdown()

    async def _startup(self):
        await self.docker_sandbox.start()
        self.console.print(Panel.fit(
            f"{__name__}\n\n"
            "[bold cyan]AI Assistant Command Line Interface[/bold cyan]\n"
            "Type [bold]help[/bold] for available commands\n"
            "Type [bold]exit[/bold] or [bold]quit[/bold] to exit\n"
            "\n"
            "[dim]• Chat mode: Just type anything[/dim]\n"
            "[dim]• Tasks: [bold]task <description>[/bold][/dim]\n"
            "[dim]• Commands: [bold]shell|python|system <command>[/bold][/dim]",
            title="Welcome",
            border_style="blue"
        ))

    async def _shutdown(self):
        await self._cleanup()

    async def _loop(self):
        while self._running:
            try:
                user_input = await self._read_input()
                if not user_input:
                    continue
                result = await self._process_command(user_input)
                if result == "exit":
                    self._running = False
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def _read_input(self):
        try:
            text = self.console.input("[bold blue]>>> [/bold blue]")
        except (EOFError, KeyboardInterrupt):
            return "exit"
        return text.strip()

    async def _process_command(self, user_input: str):
        """Processing user input commands"""

        parts = shlex.split(user_input)
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        # Command distribution 
        if cmd == "help": 
            self._show_help()
        elif cmd in {"exit", "quit"}:
            self.console.print("[yellow]Goodbye![/yellow]")
            return "exit"
        elif cmd == "shell": 
            await self._handle_shell_command(args)
        elif cmd == "python": 
            await self._handle_python_command(args)
        elif cmd == "system": 
            await self._handle_system_command(args)
        elif cmd == "task": 
            await self._plan_and_confirm(' '.join(args))
        elif cmd == "resume_run": 
            await self._handle_resume_run(run_id = args[0])
        elif cmd == "replay_failed": 
            await self._handle_replay_failed(run_id = args[0])
        elif cmd == "clear": 
            self._handle_clear_command()
        elif cmd == "history": 
            self._show_history()
        else:
            await self._chat(user_input)
    async def _chat(self, user_input: str):
        msg = InboundMessage(
            channel = "cli", 
            sender_id = "user", 
            conversation_id = "main", 
            content = user_input
            )
        response = await self.conversation_service.handle_message(msg)
        content = Markdown(response.content)
        self.console.print()
        self.console.print(content)
        self.console.print()


    async def _plan_and_confirm(self, user_input: str):
        """
        Planning-Confirmation-Execution Process
        This is the core function of a planned task.
        """
        # 1. Generate plan
        self.console.print("[bold cyan]📝 Generating execution plan...[/bold cyan]")
        plan = await self.dag_planner.plan(user_input)
        plan_tasks = plan["tasks"]
        
        if not plan_tasks:
            self.console.print("[red]❌ Could not generate a plan for your input[/red]")
            return
            
        self.last_plan_tasks = plan_tasks
        
        # 2. Display plan
        self.console.print("\n[bold]Generated Plan:[/bold]")
        self.console.print(self.last_plan_tasks)
        # 3. Request user confirmation
        self.console.print("\n[yellow]Do you want to execute this plan?[/yellow]")
        confirm = Confirm.ask("[bold]Execute?[/bold]", default=True)
        
        if confirm:
            # 4. Execute after user confirmation
            self.console.print("[green]✓ Plan confirmed, starting execution...[/green]")
            await self._execute_plan(plan_tasks)
        else:
            # 5. The user has not confirmed; modifications can be made before execution.
            self.console.print("[yellow]⏸️ Plan execution cancelled[/yellow]")
            run_id, run_dir = self.dag_scheduler.save_dag(plan_tasks)
            self.console.print("[cyan]run_id[/cyan]:", run_id)
            self.console.print("[cyan]run_dir[cyan]:", run_dir)
            self.console.print("You can:")
            self.console.print("Modify the task plan in  [cyan]dag.json[/cyan]")
            self.console.print(f"Then restart the task with [cyan]resume_run {run_id}[/cyan]")
 
    
    async def _execute_plan(self, plan_tasks):
        """Execute planned tasks"""
        result = await self.dag_scheduler.run(plan_tasks)
        self.console.print("[bold green]✅ Plan execution completed![/bold green]")



    async def _handle_resume_run(self, run_id):
        self.console.print("[bold green]Plan resume run start![/bold green]")
        await self.dag_scheduler.resume(run_id = run_id)
        self.console.print("[bold green]✅ Plan resume run completed![/bold green]")

    async def _handle_replay_failed(self, run_id):
        self.console.print("[bold green]✅ Plan replay failed start![/bold green]")
        await self.dag_scheduler.replay_failed(run_id = run_id)
        self.console.print("[bold green]✅ Plan replay failed completed![/bold green]")

    async def _handle_shell_command(self, args: List[str]):
        """Processing Shell commands"""
        if not args:
            self.console.print("[red]Usage: shell <command>[/red]")
            return
            
        command = " ".join(args)
        cmd = Command(
            type=CommandType.SHELL,
            name=f"shell_{len(self.command_history)}",
            content=command
        )
        await self._execute_command(cmd)
        
    async def _handle_python_command(self, args: List[str]):
        """Processing Python commands"""
        if not args:
            self.console.print("[red]Usage: python <code>[/red]")
            self.console.print("       python -m <module>")
            self.console.print("       python -f <file>")
            return
            
        if args[0] == "-m":
            if len(args) < 2:
                self.console.print("[red]Usage: python -m <module>[/red]")
                return
            content = f"import {args[1]}"
        elif args[0] == "-f":
            if len(args) < 2:
                self.console.print("[red]Usage: python -f <file>[/red]")
                return
            try:
                with open(args[1], 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                self.console.print(f"[red]File not found: {args[1]}[/red]")
                return
        else:

            content = " ".join(args)
            
        cmd = Command(
            type=CommandType.PYTHON,
            name=f"python_{len(self.command_history)}",
            content=content
        )
        await self._execute_command(cmd)
        
    async def _handle_system_command(self, args: List[str]):
        """Processing system commands"""
        if not args:
            self.console.print("[red]Usage: system <command>[/red]")
            return
            
        command = " ".join(args)
        cmd = Command(
            type=CommandType.SYSTEM,
            name=f"system_{len(self.command_history)}",
            content=command
        )
        await self._execute_command(cmd)
        
        
    def _handle_clear_command(self):
        """clear screen"""
        self.console.clear()
        
    def _show_history(self):
        """Show command history"""
        if not self.command_history:
            self.console.print("[yellow]No command history[/yellow]")
            return
            
        table = Table(title="Command History")
        table.add_column("#", style="cyan")
        table.add_column("Command", style="green")
        
        start = max(0, len(self.command_history) - 10)
        for i in range(start, len(self.command_history)):
            table.add_row(str(i + 1), self.command_history[i])
            
        self.console.print(table)
        
            
    def _show_help(self):
        """Display help information"""
        help_text = """
    [bold cyan]Available Commands:[/bold cyan]

    [bold]Basic Commands:[/bold]
    [green]help[/green]                    - Show this help message
    [green]exit[/green] / [green]quit[/green]            - Exit the tool
    [green]clear[/green]                   - Clear screen
    [green]history[/green]                 - Show command history

    [bold]Execution Commands:[/bold]
    [green]shell <command>[/green]         - Execute shell command (non-blocking)
    [green]python <code>[/green]           - Execute Python code
    [green]system <command>[/green]        - Execute system command (blocking)
    [green]<any text>[/green]              - Chat mode (default behavior)

    [bold]Task Planning:[/bold]
    [green]task <description>[/green]      - Generate and execute a plan for the task
    [green]resume_run <run_id>[/green]     - Resume execution of a specific task run
    [green]replay_failed <run_id>[/green]  - Replay failed tasks from a specific run

    [bold]Workflow Example:[/bold]
    [cyan]>>> task create a backup of all .txt files[/cyan]
    [dim]# System generates plan and executes it automatically[/dim]
    [cyan]>>> replay_failed run_123[/cyan]
    [dim]# Replays only the failed tasks from run_123[/dim]
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        
    async def _execute_command(self, command: Command):
        """Execute commands in the sandbox"""
        self.command_history.append(command.content)
        
        self.console.print(f"[cyan]Executing: {command.name}[/cyan]")
        self.console.print(f"[dim]Command: {command.content}[/dim]")
        
        try:
            result = await self.docker_sandbox.execute(command.content)
            

            if result:
                self.console.print("[bold green]Output:[/bold green]")
                
                lines = result.split('\n')
                for line in lines:
                    if line.strip():  
                        self.console.print(f"  [white]{line}[/white]")
                    else:
                        self.console.print("")  
            else:
                self.console.print("[yellow]Command executed successfully (no output)[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Error executing command: {str(e)}[/red]")
    async def _cleanup(self):
        """Clean up resources"""
        try:
            await self.docker_sandbox.stop()
        except:
            pass

  