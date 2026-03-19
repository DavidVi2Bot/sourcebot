# sourcebot/storage/rules_loader.py
from pathlib import Path
from typing import List, Optional

# logger = logging.getLogger(__name__)

class RulesLoader:
    """Load rules files."""
    def __init__(self, app_root_path: Path):
        self.rules_path = [app_root_path/"rules"]
        self.rules_common_path = app_root_path / "rules/common"
        
    def load_common_rules(self) -> str:
        """Load all .md files from rules/common"""
        parts = []
        if self.rules_common_path.exists() and self.rules_common_path.is_dir():
            for file_path in self.rules_common_path.glob("*.md"):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        parts.append(content)
                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")
        return "\n\n".join(parts) if parts else ""


    def list_rules_dirs(self) -> List[str]:
        '''List rules other than common.'''
        result = set()

        for root in self.rules_path:
            if not root:
                continue

            root = Path(root).expanduser()

            if not root.exists():
                continue

            for d in root.iterdir():
                if d.is_dir() and d.name != "common":
                    result.add(d.name)

        return sorted(result)
    

    def read_rule(self, name: str) -> Optional[str]:
        """Read by name rules + common."""
        contents = []

        for root in self.rules_path:
            root = Path(root).expanduser()

            for rule_name in ["common", name]:

                target_dir = root / rule_name

                if not target_dir.is_dir():
                    continue

                for md in sorted(target_dir.glob("*.md")):
                    try:
                        text = md.read_text("utf-8")
                        contents.append(f"# {md.stem}\n\n{text}")
                    except Exception:
                        pass

        if contents:
            return "\n\n---\n\n".join(contents)

        return None
    