# sourcebot/context/skill/skill_requirements.py

import os, shutil
from sourcebot.context.skill.skill import Skill

def check_requirements(skill: Skill) -> bool:
    req = skill.requirements or {}
    for b in req.get("bins", []):
        if not shutil.which(b):
            return False
    for e in req.get("env", []):
        if not os.environ.get(e):
            return False
    return True

def missing_requirements(skill: Skill) -> str:
    req = skill.requirements or {}
    missing = []
    for b in req.get("bins", []):
        if not shutil.which(b):
            missing.append(f"CLI:{b}")
    for e in req.get("env", []):
        if not os.environ.get(e):
            missing.append(f"ENV:{e}")
    return ", ".join(missing)