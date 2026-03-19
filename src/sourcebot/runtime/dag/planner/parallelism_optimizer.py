# sourcebot/planning/parallelism_optimizer.py

from typing import Dict, List
import re


class ParallelismOptimizer:

    def __init__(self):
        pass

    def build_dependencies(self, steps: List[str]) -> Dict[int, List[int]]:
        """
        return:
        step_index -> depends_on
        """
        deps = {}
        for i, step in enumerate(steps):
            deps[i] = []
            for j in range(i):
                if self._has_dependency(steps[j], step):
                    deps[i].append(j)
        return deps

    def _has_dependency(self, a: str, b: str) -> bool:
        keywords = [
            "after",
            "based on",
            "use result",
            "then",
            "verify"
        ]
        for k in keywords:
            if k in b.lower():
                return True
        return False

    def optimize(self, tasks):
        # remove redundant dependencies
        for t in tasks:
            deps = set(t.get("depends_on", []))
            # simple dedup
            t["depends_on"] = list(deps)
        return tasks