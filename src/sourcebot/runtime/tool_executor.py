# sourcebot/runtime/tool_executor.py

import asyncio
class ToolExecutor:

    def __init__(self, tools, timeout = 60, retries = 2):
        self.tools = tools
        self.timeout = timeout
        self.retries = retries

    async def execute(self, name: str, args):

        last_error = None

        for attempt in range(self.retries + 1):

            try:

                return await asyncio.wait_for(
                    self.tools.execute(name, args),
                    timeout = self.timeout
                )

            except asyncio.TimeoutError:
                last_error = f"Tool {name} timed out"

            except Exception as e:
                last_error = str(e)

        return f"Tool failed after retries: {last_error}"