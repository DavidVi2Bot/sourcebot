
# sourcebot/context/context_builder.py
from pathlib import Path
from typing import Optional, List
from sourcebot.context.identity import get_identity
from sourcebot.context.skill import SkillLoader, SkillSummary
from sourcebot.prompt import DECOMPOSER_PROMPT, SUBAGENT_PROMPT
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Build system prompts, including identity, rules, memories, and skills."""
    def __init__(
        self, 
        workspace: Path, 
        skill_storage,
        rules_loader,
    ):
        self.workspace = workspace
        self.rules_loader = rules_loader
        self.skill_loader = SkillLoader(skill_storage)
    

    def build_chat_prompt(self):
      parts = [get_identity(str(self.workspace))]
      return "\n\n---\n\n".join(parts)
    
    # identity + rules + skill 
    def build_system_prompt(self, skill_names: Optional[List[str]] = None) -> str:
        """Assemble the complete system prompt."""

        parts = [get_identity(str(self.workspace))]
        # Bootstrap rules
        rules = self.build_rulse()
        if rules:
            parts.append(rules)

        skills_summary = self.build_skills_summary()
        if skills_summary:
            parts.append(skills_summary)
        return "\n\n---\n\n".join(parts)

    def build_subagent_prompt(self, workspace: Optional[Path] = None) -> str:
        """Build a focused system prompt for the subagent."""
        from datetime import datetime
        import time as _time
        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"

        return SUBAGENT_PROMPT.format(
                now = now,
                tz = tz,
                workspace = "/workspace"
        )


    def build_skills_summary(self) -> str: 
        all_skills = self.skill_loader.list_skills(filter_unavailable=False)
        skills_summary = SkillSummary.generate(all_skills, pretty=True)
        return f"""# Skills
The following skills extend your capabilities. To use a skill, get its SKILL.md file using the skill_detail tool.
Skills with available="false" need dependencies installed first - you can try installing them with apt/brew.
{skills_summary}"""

    def build_rulse(self, skill_names: Optional[List[str]] = None) -> str:
        return self.rules_loader.load_common_rules()

    def build_decomposer_prompt(self, skill_names: Optional[List[str]] = None) -> str:

        skills_summary = self.build_skills_summary()
        rules = self.build_rulse()

        return DECOMPOSER_PROMPT.format(
                  skills_summary = skills_summary,
                  rules = rules
              )
    
