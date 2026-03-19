# sourcebot/runtime/dag/scheduler/state_store.py
import json
from pathlib import Path
from datetime import datetime


class StateStore:

    def __init__(self, run_dir: Path):

        self.file = run_dir / "state.json"

        if self.file.exists():
            self.state = json.loads(self.file.read_text())
        else:
            self.state = {}

    def save(self):

        self.file.write_text(
            json.dumps(self.state, indent=2)
        )

    def status(self, task_id):

        return self.state.get(task_id, {}).get("status")

    def attempts(self, task_id):

        return self.state.get(task_id, {}).get("attempts", 0)

    def update(self, task_id, **fields):

        entry = self.state.setdefault(task_id, {})

        entry.update(fields)

        entry["updated_at"] = str(datetime.utcnow())

        self.save()