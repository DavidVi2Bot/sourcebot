# sourcebot/runtime/dag/scheduler/run_store.py
import json
import uuid
from pathlib import Path
from datetime import datetime


class RunStore:

    def __init__(self, runs_dir: Path):

        self.runs_dir = runs_dir
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self, tasks):

        run_id = f"run_{uuid.uuid4().hex[:8]}"

        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True)

        (run_dir / "tasks").mkdir()

        (run_dir / "dag.json").write_text(
            json.dumps(tasks, indent=2)
        )

        meta = {
            "run_id": run_id,
            "created_at": str(datetime.utcnow()),
            "status": "running"
        }

        (run_dir / "run_meta.json").write_text(
            json.dumps(meta, indent=2)
        )

        return run_id, run_dir

    def load_dag(self, run_dir):

        file = run_dir / "dag.json"

        if not file.exists():
            raise RuntimeError("dag.json missing")

        return json.loads(file.read_text())

    def update_status(self, run_dir, status):

        meta_file = run_dir / "run_meta.json"

        meta = json.loads(meta_file.read_text())

        meta["status"] = status
        meta["updated_at"] = str(datetime.utcnow())

        meta_file.write_text(json.dumps(meta, indent=2))