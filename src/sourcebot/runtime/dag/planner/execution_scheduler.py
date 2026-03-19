# sourcebot/planning/execution_scheduler.py
# DAG → Execution Levels

from typing import List, Dict


class ExecutionScheduler:

    def build_levels(self, tasks: List[Dict]) -> List[List[Dict]]:
        """
        Convert DAG tasks into execution levels
        """

        remaining = {t["id"]: set(t.get("depends_on", [])) for t in tasks}
        task_map = {t["id"]: t for t in tasks}

        levels = []

        while remaining:

            ready = [tid for tid, deps in remaining.items() if not deps]

            if not ready:
                raise RuntimeError("Cycle detected in DAG")

            level_tasks = [task_map[r] for r in ready]
            levels.append(level_tasks)

            for r in ready:
                remaining.pop(r)

            for deps in remaining.values():
                deps.difference_update(ready)

        return levels