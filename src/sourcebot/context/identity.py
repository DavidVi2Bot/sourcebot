# sourcebot/context/identity.py
from sourcebot.prompt import IDENTITY_PROMPT
from datetime import datetime
import platform
import time

def get_identity(workspace_path: str) -> str:
    """Return bot identity/system prompt header."""
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (%A)")
    tz = time.strftime("%Z") or "UTC"
    system = platform.system()
    runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

    return IDENTITY_PROMPT.format(
                now = now,
                tz = tz,
                runtime = runtime,
                workspace_path = "/workspace"
            )
