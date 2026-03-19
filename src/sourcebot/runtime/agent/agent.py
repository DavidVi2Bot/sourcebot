# sourcebot/runtime/agent_runtime.py 
import json
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import logging
from sourcebot.security.policy import SecurityPolicy
from sourcebot.tools.registry import ToolRegistry
from sourcebot.context import MessageBuilder
from sourcebot.utils import strip_think, parse_tool_args, ensure_string
from datetime import datetime
from sourcebot.runtime import ToolExecutor
from sourcebot.bus import EventBus, OutboundMessage

logger = logging.getLogger(__name__)
class Agent:
    """
    A unified runtime environment for the main agent and sub-agents.
    Supports:
    - LLM loop
    - Tool execution
    - Policy hooks
    - Message bus # TODO
    """

    def __init__(
        self,
        bus: EventBus,
        llm,
        tools: ToolRegistry,
        message_builder: MessageBuilder,
        policy: Optional[SecurityPolicy] = None,
        task_id: Optional[str] = None,
        task_description: Optional[str] = None,
        max_tool_calls: int = 40,
        max_iterations: int = 40,
    ):
        self.bus = bus
        self.llm = llm
        self.tools = tools
        self.message_builder = message_builder
        self.policy = policy
        self.task_id = task_id
        self.task_description = task_description
        # Limits
        self.max_tool_calls = max_tool_calls
        self.max_iterations = max_iterations

        self.tool_executor = ToolExecutor(
            tools,
            timeout = 60,
            retries = 2
        )


    async def run(
        self,
        messages: List[Dict[str, Any]],
        use_tools: bool = True,
        use_policy: bool = True,
    ):
        """
        agent loop
        """
        tools_used: list[str] = []
        tool_counter = 0
        logger.info(f"{self.task_id} Running")
        for i in range(self.max_iterations):

            # Policy before llm
            if self.policy and use_policy:
                await self.policy.before_llm(messages)

            response = await self.llm.complete(
                messages = messages,
                tools = self.tools.get_definitions(),
            )
            # # Response adapter
            llm_tool_calls = response.tool_calls

            # Tool calls
            if llm_tool_calls and use_tools:

                messages = self.message_builder.add_assistant_message(
                    messages = messages,
                    content = response.content,
                    tool_calls = llm_tool_calls,
                )
                for tool_call in llm_tool_calls:
                    tool_name = tool_call.name

                    tools_used.append(tool_name)

                    tool_counter += 1
                    if tool_counter > self.max_tool_calls:
                        raise RuntimeError("Exceeded max tool calls")
                    args = parse_tool_args(tool_call.arguments)

                    # Policy before tool
                    if self.policy and use_policy:
                        await self.policy.before_tool(tool_name, args)

                    result = await self.tool_executor.execute(
                        tool_name,
                        args
                    )

                    # Policy after tool
                    if self.policy and use_policy:
                        await self.policy.after_tool(
                            tool_name,
                            result,
                        )

                    messages = self.message_builder.add_tool_result(
                        messages = messages,
                        tool_call_id = tool_call.id,
                        result = ensure_string(result), 
                    )
  
            # Final response
            else:
                logger.info(f"{self.task_id} Completed")

                final = strip_think(response.content)

                return final, self.task_id, tools_used
        
        raise RuntimeError("Max iterations exceeded")


