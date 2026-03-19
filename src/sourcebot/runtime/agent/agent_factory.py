# sourcebot/runtime/agent/agent_factory.py
from sourcebot.runtime.agent import Agent
from typing import Optional
from pathlib import Path
from sourcebot.tools import ToolRegistry
from sourcebot.llm import LLMClientFactory

import logging
logger = logging.getLogger(__name__)
class AgentFactory:
    """
    Factory responsible for building Agent instances
    for both main agent and subagents.
    """

    def __init__(
        self,
        bus,
        message_builder,
        policy,
        main_provider_name,
        main_model_name, 
        config_manager,
        max_tool_calls: int = 40,
        max_iterations: int = 40,
        sub_provider_name: Optional[str] = None,
        sub_model_name: Optional[str] = None,
        tools: Optional[ToolRegistry] = None,
    ):
        self.bus = bus
        self.message_builder = message_builder
        self.policy = policy
        self.main_provider_name = main_provider_name
        self.main_model_name = main_model_name
        self.config_manager = config_manager
        self.sub_provider_name = sub_provider_name
        self.sub_model_name = sub_model_name
        self.max_tool_calls = max_tool_calls
        self.max_iterations = max_iterations
        self.tools = tools
        
    def build_main_agent(self) -> Agent:
        """
        Build main agent.
        """
        llm = LLMClientFactory.create_client(
            config_manager = self.config_manager,
            provider_name = self.main_provider_name,
            model_name = self.main_model_name
        )
        return Agent(
            bus = self.bus,
            llm = llm,
            tools = self.tools,
            message_builder = self.message_builder,
            policy = self.policy,
            max_tool_calls = self.max_tool_calls,
            max_iterations = self.max_iterations,
            task_id = "main_agent"
        )

    def build_sub_agent(self, task_id, task_description) -> Agent:
        """
        Build sub agent.
        """
        llm = LLMClientFactory.create_client(
            config_manager = self.config_manager,
            provider_name = self.sub_provider_name or self.main_provider_name,
            model_name = self.sub_model_name or self.main_model_name
        )
        return Agent(
            bus = self.bus,
            tools = self.tools,
            llm = llm,
            message_builder = self.message_builder,
            policy = self.policy,
            task_id = task_id,
            task_description = task_description,
            max_tool_calls = self.max_tool_calls,
            max_iterations = self.max_iterations,
        )


