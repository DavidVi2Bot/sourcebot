# sourcebot/docker_sandbox/dockersandbox.py
import asyncio
import docker
import shlex
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
class DockerSandbox:
    def __init__(
        self,
        image: str = "python:3.11-slim",
        workdir: str = "/workspace",          # Working directory within the container
        host_workspace: str | None = None,    # Host directory
    ):
        self.client = docker.from_env()
        self.image = image
        self.workdir = workdir
        if not host_workspace:
            raise ValueError("host_workspace must be provided")
        self.host_workspace = str(Path(host_workspace).resolve())
        Path(self.host_workspace).mkdir(parents=True, exist_ok=True)
        self.container = None

    # Secure Start (async wrapper)
    async def start(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._start_sync)

    def _start_sync(self):
        logger.debug(f"Starting Docker sandbox with image {self.image}")
        logger.debug(f"Host workspace: {self.host_workspace}")

        try:
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {self.image}")
                self.client.images.pull(self.image)

            self.container = self.client.containers.create(
                self.image,
                command="sleep infinity",
                tty=True,
                volumes={
                    self.host_workspace: {
                        "bind": self.workdir,
                        "mode": "rw",
                    }
                },
                working_dir=self.workdir,
            )
            self.container.start()
            logger.debug(f"Docker sandbox started: {self.container.id}")

        except Exception as e:
            logger.error(f"Failed to start Docker sandbox: {e}")
            self.container = None
            raise

    async def execute(self, cmd: str, timeout: Optional[int] = 300) -> str:
        """
        Execute commands in a Docker container
        """
        if not self.container:
            raise RuntimeError("DockerSandbox not started")
        
        logger.debug(f"Executing command in Docker: {cmd}")
        exec_instance = self.client.api.exec_create(
            container = self.container.id,
            cmd = ["bash", "-c", cmd],
            workdir = self.workdir,
            stdout = True,
            stderr = True,
            tty = True,
        )
        output = self.client.api.exec_start(exec_instance['Id'], detach=False, tty=True)
        exit_code = self.client.api.exec_inspect(exec_instance['Id'])['ExitCode']

        result = output.decode("utf-8").strip()
        if exit_code != 0:
            logger.warning(f"Command failed (exit {exit_code}): {result}")
        else:
            logger.debug(f"Command succeeded: {result}")
        return result


    # Safe stop
    async def stop(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._stop_sync)

    def _stop_sync(self):
        if self.container:
            logger.debug(f"Stopping Docker sandbox {self.container.id}")
            try:
                self.container.kill()
            except Exception as e:
                logger.warning(f"Error killing container: {e}")
            try:
                self.container.remove(force=True)
            except Exception as e:
                logger.warning(f"Error removing container: {e}")
            self.container = None
            logger.debug("Docker sandbox stopped")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()