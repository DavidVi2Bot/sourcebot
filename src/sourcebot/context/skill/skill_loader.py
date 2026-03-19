# sourcebot/context/skill/skill_loader.py
from typing import List, Optional
from sourcebot.context.skill.skill import Skill
from sourcebot.context.skill.skill_metadata import SkillMetadataParser
from sourcebot.context.skill.skill_requirements import check_requirements
from sourcebot.storage.skill_storage import SkillStorage
from sourcebot.context.skill.skill_context import strip_frontmatter

class SkillLoader:
    """Load skills as Skill instances."""
    def __init__(self, skill_storage: SkillStorage):
        self.skill_storage = skill_storage
        self._cache: dict[str, Skill] = {}

    def list_skills(self, filter_unavailable: bool = True) -> List[Skill]:
        skills: List[Skill] = []
        for name, path, source in self.skill_storage.list_skill_dirs(source = "all"):
            content = path.read_text(encoding="utf-8")
            meta = SkillMetadataParser.parse(content)
            skill = Skill(
                name=name,
                description=meta.get("description", name),
                content=content,
                requirements=meta.get("requires", {}),
                always=meta.get("always", False),
                source=source
            )
            if not filter_unavailable or check_requirements(skill):
                skills.append(skill)
                self._cache[name] = skill
        return skills

    def load_skill(self, name: str) -> Optional[Skill]:
        if name in self._cache:
            return self._cache[name]
        content = self.skill_storage.read_skill(name)
        if not content:
            return None
        meta = SkillMetadataParser.parse(content)
        skill = Skill(
            name=name,
            description=meta.get("description", name),
            content=content,
            requirements=meta.get("requires", {}),
            always=meta.get("always", False),
            source="root"
        )
        self._cache[name] = skill
        return skill

    def load_skills_for_context(self, skill_names: List[str]) -> str:
        parts = []
        for name in skill_names:
            skill = self.load_skill(name)
            if skill:
                parts.append(f"### Skill: {skill.name}\n\n{strip_frontmatter(skill.content)}")
        return "\n\n---\n\n".join(parts) if parts else ""