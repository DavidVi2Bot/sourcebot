# sourcebot/skill/skill.py
from dataclasses import dataclass

@dataclass
class Skill:
    name: str
    description: str
    content: str
    requirements: dict
    always: bool = False
    source: str = "root"