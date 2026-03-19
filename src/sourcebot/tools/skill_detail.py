# sourcebot/tools/skill_detail.py
from sourcebot.tools.base import Tool
from typing import Any, Optional
from pathlib import Path
class SkillDetailTool(Tool):
    """Return to skill details"""
    
    def __init__(
        self,
        skill_storage,
        host_workspace,
    ):
        self.skill_storage = skill_storage
        self.host_workspace = host_workspace
    @property
    def name(self) -> str:
        return "skill_detail"

    @property
    def description(self) -> str:
        return (
            "Get the details corresponding to the skill name"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string", 
                    "description": "The name of the skill to get details for",
                },
            },
            "required": ["name"],
        }


    async def execute(
        self, 
        name: str,  # Default to skills directory
        **kwargs: Any,
    ) -> str:
        """
        Execute the tool and return the skill details.

        Args:
            name: Skill name
        Returns:
            A string containing the skill details
        """
        try:
            
            self.skill_storage.inject_skill(name, self.host_workspace)
            skill_content = self.skill_storage.read_skill(name)
            guide_message = f"\n\nSkill data has been injected into /workspace/skills/{name} directory for your reference and use."
    
            return skill_content + guide_message
        except Exception as e:
            return f"Error reading skill details: {str(e)}"
        