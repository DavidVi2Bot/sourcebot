# sourcebot/tools/skill_list.py
from sourcebot.tools.base import Tool
from typing import Any, Optional

class SkillListTool(Tool):
    """Return to the list of available skills"""
    
    def __init__(
        self,
        skill_storage,
    ):
        self.skill_storage = skill_storage
    @property
    def name(self) -> str:
        return "skill_list"

    @property
    def description(self) -> str:
        return (
            "Return to the skill list.Directly calling this tool will return to the skill catalog list."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string", 
                    "description": "The directory path to list",
                    "default": "/skills"  # Set default path to skills directory
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recursively list all files (default false)",
                },
                "max_entries": {
                    "type": "integer",
                    "description": "Maximum entries to return (default 200)",
                    "minimum": 1,
                },
            },
            # Make path optional since we have a default
            "required": [],
        }

    async def execute(
        self, 
        path: str = "/skills",  # Default to skills directory
        recursive: bool = False,
        max_entries: int | None = None, 
        **kwargs: Any,
    ) -> str:
        """
        Execute the tool and return directory listing.
        
        Args:
            path: Directory path to list (defaults to /skills)
            recursive: Whether to list recursively
            max_entries: Maximum number of entries to return
            
        Returns:
            String containing directory listing
        """
        try:
            return self.skill_storage.list_skill_name(source = "all")
        except Exception as e:
            return f"Error geting skill list: {str(e)}"