# sourcebot/skill/skill_metadata.py
import re, json
from typing import Dict

class SkillMetadataParser:
    """Parse YAML/JSON frontmatter from skill markdown files."""
    FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

    @classmethod
    def parse(cls, content: str) -> Dict:
        match = cls.FRONTMATTER_RE.match(content)
        if not match:
            return {}
        front = match.group(1)
        metadata = {}
        for line in front.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip().strip('"\'')
        raw_meta = metadata.get("metadata")
        if raw_meta:
            try:
                data = json.loads(raw_meta)
                return data.get("sourcebot", data.get("openclaw", {}))
            except (json.JSONDecodeError, TypeError):
                return {}
        return metadata