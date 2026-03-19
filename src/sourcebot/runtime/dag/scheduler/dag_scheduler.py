# sourcebot/runtime/dag/scheduler/dag_scheduler.py
import asyncio
import json
import logging
from pathlib import Path
from collections import deque
from datetime import datetime
from sourcebot.runtime.dag.scheduler.task_graph import TaskGraph
from sourcebot.runtime.dag.scheduler.state_store import StateStore
from sourcebot.runtime.dag.scheduler.retry_policy import RetryPolicy
from sourcebot.runtime.dag.scheduler.run_store import RunStore
from sourcebot.llm.core.message import Message

logger = logging.getLogger(__name__)


class DAGScheduler:

    def __init__(
        self,
        agent_factory,
        workspace,
        runs_dir="runs",
        max_concurrent=4,
        retry_policy=None,
        
    ):

        self.agent_factory = agent_factory

        self.runs_dir = Path(workspace)/runs_dir

        self.max_concurrent = max_concurrent

        self.retry_policy = retry_policy or RetryPolicy()

        self.semaphore = asyncio.Semaphore(max_concurrent)

        self.run_store = RunStore(self.runs_dir)

    # Run DAG
    async def run(self, tasks):

        self.run_id, self.run_dir = self.run_store.create_run(tasks)

        logger.info(f"DAG RUN {self.run_id}")

        self.state = StateStore(self.run_dir)

        graph = TaskGraph(tasks)

        result = await self._execute(graph)

        if result["failed"]:
            self.run_store.update_status(self.run_dir, "failed")
        else:
            self.run_store.update_status(self.run_dir, "completed")

        return result

    # Resume run
    async def resume(self, run_id):

        self.run_id = run_id
        self.run_dir = self.runs_dir / run_id

        tasks = self.run_store.load_dag(self.run_dir)

        self.state = StateStore(self.run_dir)

        graph = TaskGraph(tasks)

        logger.info(f"Resuming {run_id}")

        return await self._execute(graph)


    # Replay failed tasks
    async def replay_failed(self, run_id):

        self.run_id = run_id
        self.run_dir = self.runs_dir / run_id

        tasks = self.run_store.load_dag(self.run_dir)

        self.state = StateStore(self.run_dir)

        for t in list(self.state.state.keys()):

            if self.state.state[t]["status"] == "failed":
                self.state.state[t]["status"] = "pending"

        self.state.save()

        graph = TaskGraph(tasks)

        logger.info(f"Replay failed tasks {run_id}")

        return await self._execute(graph)


    # Core execution
    async def _execute(self, graph):

        ready = deque()

        running = {}

        future_map = {}

        completed = set()
        failed = set()

        for tid, deg in graph.in_degree.items():

            state = self.state.status(tid)

            if state == "completed":
                completed.add(tid)
                continue

            if deg == 0:
                ready.append(tid)

        while ready or running:

            while ready and len(running) < self.max_concurrent:

                tid = ready.popleft()

                task = graph.tasks[tid]

                fut = asyncio.create_task(
                    self._execute_task(task)
                )

                running[tid] = fut
                future_map[fut] = tid

            if not running:
                break

            done, _ = await asyncio.wait(
                running.values(),
                return_when=asyncio.FIRST_COMPLETED
            )

            for fut in done:

                tid = future_map[fut]

                try:

                    result = fut.result()

                    if result["success"]:

                        completed.add(tid)

                        for child in graph.children[tid]:

                            graph.in_degree[child] -= 1

                            if graph.in_degree[child] == 0:
                                ready.append(child)

                    else:
                        failed.add(tid)

                except Exception as e:

                    failed.add(tid)
                    logger.error(f"{tid} crashed: {e}")

                del running[tid]

        return {
            "completed": list(completed),
            "failed": list(failed)
        }


    # Task execution
    async def _execute_task(self, task):

        task_id = task["id"]

        log_file = self.run_dir / "tasks" / f"{task_id}.log"

        attempt = self.state.attempts(task_id) + 1

        while True:

            try:

                self.state.update(
                    task_id,
                    status = "running",
                    attempts = attempt,
                    started = str(datetime.utcnow())
                )

                async with self.semaphore:

                    agent = self.agent_factory.build_sub_agent(
                        task_id = task_id,
                        task_description = task["description"]
                    )
                    messages = self._build_messages(task)
                    result, _, _ = await agent.run(messages)

                self._write_log(log_file, result)

                if self._is_success(result):

                    self.state.update(
                        task_id,
                        status = "completed",
                        result = result
                    )

                    return {"success": True}

                raise RuntimeError("task failed")

            except Exception as e:

                self._write_log(log_file, str(e))

                if not self.retry_policy.should_retry(attempt):

                    self.state.update(
                        task_id,
                        status = "failed",
                        error = str(e)
                    )

                    return {"success": False}

                delay = self.retry_policy.get_delay(attempt)

                logger.warning(
                    f"{task_id} retry in {delay}s"
                )

                await asyncio.sleep(delay)

                attempt += 1

    # =================================
    # Helpers
    # =================================

    def _write_log(self, file: Path, data):

        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "a") as f:

            f.write(
                f"\n[{datetime.utcnow()}]\n"
            )

            if isinstance(data, str):
                f.write(data + "\n")
            else:
                f.write(json.dumps(data, indent=2) + "\n")

    def _is_success(self, result):

        if isinstance(result, dict):
            return result.get("success", True)

        return bool(result)

    def _build_messages(self, task):
        return [
            Message(role = "system", content = f"You are executing task {task['id']}"),
            Message(role = "user", content = self.build_task_description(task)),
        ]

    def build_task_description(self, task):
        """Combine the task and context into a complete description."""
        description = task.get("description", "")
        context = task.get("context", {})
        
        context_parts = []
        
        if context.get("rules"):
            rules = "\n  • ".join(context["rules"])
            context_parts.append(f"Rules:\n  • {rules}")
        
        if context.get("skills"):
            skills = ", ".join(context["skills"])
            context_parts.append(f"Required skills: {skills}")
        
        if context.get("environment"):
            env = context["environment"]
            if env.get("required_tools"):
                tools = ", ".join(env["required_tools"])
                context_parts.append(f"Required tools: {tools}")
            if env.get("working_dir"):
                context_parts.append(f"Working directory: {env['working_dir']}")
        
        if context.get("inherited_context"):
            inherited = context["inherited_context"]
            inherited_items = [f"{k}: {v}" for k, v in inherited.items()]
            context_parts.append(f"Context: {', '.join(inherited_items)}")
        
        if context_parts:
            full_description = f"{description}\n\nContext Information:\n" + "\n".join(context_parts)
        else:
            full_description = description
        
        return full_description


    def save_dag(self, plan_tasks):
        return self.run_store.create_run(plan_tasks)