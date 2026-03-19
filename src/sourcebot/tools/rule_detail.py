# sourcebot/tools/rule_detail.py
from sourcebot.tools.base import Tool
from typing import Any, Optional
from pathlib import Path


class RuleDetailTool(Tool):
    """Tool for retrieving detailed information about a specific rule."""
    
    def __init__(self, rules_loader):
        """
        Initialize the RuleDetailTool.
        
        Args:
            rules_loader: Loader instance for accessing rules
        """
        self.rules_loader = rules_loader

    @property
    def name(self) -> str:
        return "rule_detail"

    @property
    def description(self) -> str:
        return (
            "Get detailed information about a specific rule. "
            "Provide the rule name to retrieve its full content and requirements."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string", 
                    "description": "The name of the rule to get details for",
                },
            },
            "required": ["name"],
        }

    async def execute(self, name: str, **kwargs: Any) -> str:
        """
        Execute the tool and return detailed information about a specific rule.
        
        Args:
            name: The name of the rule to retrieve
            
        Returns:
            A string containing the rule details, or an error message if not found
        """
        try:
            # Validate input
            if not name or not isinstance(name, str):
                return "Error: Rule name must be a non-empty string"
            
            # Read rule content
            rule_content = self.rules_loader.read_rule(name)
            
            if not rule_content:
                return f"No content found for rule: {name}"
            
            # Format the output
            return f"=== Rule: {name} ===\n\n{rule_content}\n\n=== End of Rule ==="
            
        except FileNotFoundError:
            return f"Error: Rule '{name}' not found. Use the rules_list tool to see available rules."
        except Exception as e:
            return f"Error reading rule details for '{name}': {str(e)}"