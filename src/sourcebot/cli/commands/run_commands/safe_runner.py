# sourcebot/cli/commands/safe_runner.py
import inspect
import asyncio

class SafeRunner:
    def __init__(self, obj):
        self.obj = obj

        # case 1: async function
        if inspect.iscoroutinefunction(obj):
            self.mode = "async_function"
            return

        # case 2: coroutine
        if inspect.iscoroutine(obj):
            self.mode = "coroutine"
            return

        # case 3: factory function 
        if callable(obj) and not inspect.isclass(obj):
            obj = obj()

        self.obj = obj

        # case 4: class instance with run()
        if hasattr(self.obj, "run") and callable(self.obj.run):
            self.mode = "runner"
            self.is_async = inspect.iscoroutinefunction(self.obj.run)
            return

        raise TypeError(f"{type(obj)} is not runnable")

    async def run(self, *args, **kwargs):
        # async function
        if self.mode == "async_function":
            return await self.obj(*args, **kwargs)

        # coroutine
        if self.mode == "coroutine":
            return await self.obj

        # class with run()
        if self.mode == "runner":
            if self.is_async:
                return await self.obj.run(*args, **kwargs)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: self.obj.run(*args, **kwargs))