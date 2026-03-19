# sourcebot/tools/rule_list.py
from sourcebot.tools.base import Tool
from typing import Any, Optional


class RuleListTool(Tool):
    """Tool for listing available rules that need to be followed."""
    
    def __init__(self, rules_loader):
        """
        Initialize the RuleListTool.
        
        Args:
            rules_loader: Loader instance for accessing rules
        """
        self.rules_loader = rules_loader

    @property
    def name(self) -> str:
        return "rule_list"

    @property
    def description(self) -> str:
        return (
            "Returns the list of available rules. "
            "Call this tool to see all rules that must be followed."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool and return the list of available rules.
        
        Returns:
            String containing the list of rules
        """
        try:
            rule_list = self.rules_loader.list_rules_dirs()
            
            if not rule_list:
                return "No rules found."
            
            lines = ["Available rules:"]
            for i, rule in enumerate(rule_list, 1):
                lines.append(f"{i}. {rule}")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error getting rules list: {str(e)}"