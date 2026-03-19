# sourcebot/skill/skill_context.py
import re

def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith("---"):
        match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if match:
            return content[match.end():].strip()
    return content