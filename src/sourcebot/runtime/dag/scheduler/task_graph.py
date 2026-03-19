# sourcebot/runtime/dag/scheduler/task_graph.py
from collections import defaultdict

class TaskGraph:

    def __init__(self, tasks):

        self.tasks = {t["id"]: t for t in tasks}

        self.children = defaultdict(list)
        self.in_degree = {}

        for t in tasks:

            tid = t["id"]
            deps = t.get("depends_on", [])

            self.in_degree[tid] = len(deps)

            for d in deps:
                self.children[d].append(tid)

    def roots(self):

        return [
            tid
            for tid, deg in self.in_degree.items()
            if deg == 0
        ]