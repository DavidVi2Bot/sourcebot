# sourcebot/planning/dag_planner.py

import uuid
from typing import List, Dict
import logging
from .task_decomposer import TaskDecomposer
from .parallelism_optimizer import ParallelismOptimizer
from .execution_scheduler import ExecutionScheduler

logger = logging.getLogger(__name__)
class DAGPlanner:

    def __init__(self, llm, context_build):

        self.decomposer = TaskDecomposer(llm, context_build)
        self.optimizer = ParallelismOptimizer()
        self.scheduler = ExecutionScheduler()

    async def plan(self, query: str):
        steps = await self.decomposer.decompose(query)
        steps = self.optimizer.optimize(steps)
        levels = self.scheduler.build_levels(steps)
        return {
            "tasks": steps,
            "levels": levels
        }