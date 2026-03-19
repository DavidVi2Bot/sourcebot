# sourcebot/storage/skill_storage.py
from pathlib import Path
from typing import Optional, List, Tuple
import shutil
class SkillStorage:
    """Read skill markdown files from disk."""
    SKILL_FILE = "SKILL.md"

    def __init__(self, root_skills: Path, builtin_skills: Optional[Path] = None):
        self.root_skills = root_skills
        self.builtin_skills = builtin_skills

    def list_skill_dirs(self, source: str) -> List[str]:
        '''List skills.'''
        result = []
        for skills_dir in [self.root_skills, self.builtin_skills]:
            if skills_dir and skills_dir.exists():
                for d in skills_dir.iterdir():
                    if d.is_dir() and (d / self.SKILL_FILE).exists():
                        result.append((d.name, d / self.SKILL_FILE, source))
        return result

    def list_skill_name(self, source: str) -> List[str]:
        '''List skills name.'''
        result = []
        for skills_dir in [self.root_skills, self.builtin_skills]:
            if skills_dir and skills_dir.exists():
                for d in skills_dir.iterdir():
                    if d.is_dir() and (d / self.SKILL_FILE).exists():
                        result.append(d.name)
        return result

    def read_skill(self, name: str) -> Optional[str]:
        """Read by name skill."""
        for skills_dir in [self.root_skills, self.builtin_skills]:
            if skills_dir and skills_dir.exists():
                f = skills_dir / name / self.SKILL_FILE
                if f.exists():
                    return f.read_text(encoding="utf-8")
        return None

    def inject_skill(self, name: str, workspace: Path):
        """Inject skills into the workspace's skills directory"""
        skill_dir = self.root_skills / name
        if not skill_dir.exists():
            return
        target = workspace / "skills" / name

        target.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(skill_dir, target, dirs_exist_ok=True)