# sourcebot/runtime/init_system.py 
from rich.console import Console
import sys
from pathlib import Path
from sourcebot.context import ContextBuilder
from sourcebot.config import ConfigManager
from sourcebot.security.policy import SecurityPolicy
from sourcebot.bus import EventBus
from sourcebot.context import MessageBuilder
from sourcebot.conversation.service import ConversationService
from sourcebot.session import JsonlSessionRepository, SessionService
from sourcebot.runtime.dag.scheduler import DAGScheduler
from sourcebot.runtime.dag.planner import DAGPlanner
from sourcebot.memory import FileMemoryStore, LLMConsolidator, MemoryService, WindowMemoryPolicy
from sourcebot.runtime.agent import AgentFactory
from sourcebot.tools import ToolRegistry, ShellTool, SkillListTool, SkillDetailTool, RuleListTool, RuleDetailTool
from sourcebot.storage import SkillStorage, RulesLoader
from sourcebot.docker_sandbox import DockerSandbox
from sourcebot.llm import LLMClientFactory
import logging
logger = logging.getLogger(__name__)

class InitSystem:
    def __init__(self):
        self.console = Console(
                    force_terminal=sys.stdout.isatty(),
                    soft_wrap=True
                ) 
        
        config_manager = ConfigManager()

        # Config 
        app_root_path = config_manager.app_root_path
        skill_dir_path = app_root_path/"skills"

        # Workspace config 
        workspace_config = config_manager.load_workspace_config() 

        # Workspace config error
        if workspace_config is None:
            self.console.print("❌ Error: Workspace configuration not found")
            self.console.print("Please run the initialization command in the root directory of the workspace first:")
            self.console.print("[cyan]sourcebot init_workspace[/cyan]")
            self.console.print("Or ensure the current directory is a valid Sourcebot workspace"
            )
            
            sys.exit(1)
        # Agent config 
        main_provider_name = workspace_config.models["main_agent"].provider
        main_model_name = workspace_config.models["main_agent"].model
        sub_provider_name = workspace_config.models["sub_agent"].provider
        sub_model_name = workspace_config.models["sub_agent"].model

        # Host working path 
        host_workspace = Path(workspace_config.project_root)

        # Docker working path 
        # The Docker working directory remains unchanged
        docker_workspace = Path("/workspace")
        # Skill storage 
        skill_storage = SkillStorage(
            root_skills = skill_dir_path,
            builtin_skills = host_workspace/"skills" # The work directory skill path should not appear in the prompt.
            )

        # Rules loader 
        rules_loader = RulesLoader(app_root_path)

        # Context builder 
        # 🔴 Note that the host machine's workspace address should not appear in the prompt; it should always be docker_workspace.
        context_builder = ContextBuilder(
            workspace = docker_workspace,  
            skill_storage = skill_storage,
            rules_loader = rules_loader,
            )

        # Message builder 
        message_builder = MessageBuilder(context_builder)

        # Security policy 
        # TODO: Security policy not yet implemented
        security_policy = SecurityPolicy()

        # Docker sandbox 
        self.docker_sandbox = DockerSandbox(
            image = workspace_config.docker_image, 
            host_workspace = str(host_workspace)
            )
        # ====================
        # Tool registry 
        # ====================
        tools = ToolRegistry()
        # Skill
        tools.register(
            SkillListTool(
                skill_storage = skill_storage,
            )
        )
        tools.register(
            SkillDetailTool(
                skill_storage = skill_storage,
                host_workspace = host_workspace,
            )
        )
        # Rule
        tools.register(
            RuleListTool(
                rules_loader = rules_loader,
            )
        )
        tools.register(
            RuleDetailTool(
                rules_loader = rules_loader,
            )
        )
        # Shell 
        tools.register(
            ShellTool(
                sandbox = self.docker_sandbox,
                timeout = 100,
            )
        )

        # Message bus 
        # TODO: Not yet enabled
        self.bus = EventBus()

        # Agent factory 
        agent_factory = AgentFactory(
            bus = self.bus,
            tools = tools,
            message_builder = message_builder,
            main_provider_name = main_provider_name,
            main_model_name = main_model_name,
            config_manager = config_manager,
            policy = security_policy,
            max_iterations = 40,
            sub_provider_name = sub_provider_name,
            sub_model_name = sub_model_name,
        )
        # DAG planner 
        main_llm = LLMClientFactory.create_client(
                config_manager = config_manager,
                provider_name = main_provider_name,
                model_name = main_model_name
            )
        self.dag_planner = DAGPlanner(main_llm, context_builder)
        # DAG scheduler 
        self.dag_scheduler = DAGScheduler(
            agent_factory = agent_factory,
            workspace = host_workspace
            )


        # Main agent runtime 
        main_agent = agent_factory.build_main_agent()

        # Memory service 
        file_memory_store = FileMemoryStore(host_workspace)
        window_memory_policy = WindowMemoryPolicy()    
        llm_consolidator = LLMConsolidator(main_llm)
        memory_service = MemoryService(
            store = file_memory_store, 
            policy = window_memory_policy,
            consolidator = llm_consolidator
            )

        # Session service 
        session_repository = JsonlSessionRepository(host_workspace)
        session_service = SessionService(session_repository)
        
        # Conversation service 
        self.conversation_service = ConversationService(
            session_service = session_service,
            memory_service = memory_service,
            agent = main_agent,
            message_builder = message_builder,
            bus = self.bus
        )



