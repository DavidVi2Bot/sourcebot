# sourcebot/tools/shell.py
"""Shell execution tool (executes commands in /workspace)"""

import os
import re
from pathlib import Path
from typing import Any, Optional

from sourcebot.tools.base import Tool
from sourcebot.docker_sandbox import DockerSandbox


class ShellTool(Tool):
    """Execute shell commands in /workspace"""

    _MAX_OUTPUT = 10_000

    def __init__(
        self,
        sandbox: DockerSandbox,
        timeout: int = 60,
        working_dir: str | None = None,
        deny_patterns: list[str] | None = None,
        allow_patterns: list[str] | None = None,
    ):
        self.sandbox = sandbox
        self.timeout = timeout
        self.working_dir = working_dir
        self.deny_patterns = deny_patterns or []
        self.allow_patterns = allow_patterns or []

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return "Execute shell commands (running in /workspace)"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to be executed",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Command timeout (seconds)",
                    "minimum": 1,
                    "maximum": 60,
                },
            },
            "required": ["command"],
        }

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Execute command (running in /workspace)"""
        

        effective_timeout = timeout or self.timeout

        try:
            # Directly call Docker Sandbox
            result = await self.sandbox.execute(
                command,
                timeout=effective_timeout,
            )

            if not result:
                result = "(no output)"

            # Truncate output length
            if len(result) > self._MAX_OUTPUT:
                half = self._MAX_OUTPUT // 2
                result = (
                    result[:half]
                    + f"\n\n... ({len(result) - self._MAX_OUTPUT:,} chars truncated) ...\n\n"
                    + result[-half:]
                )

            return result

        except Exception as e:
            return f"Command execution failed: {str(e)}"

