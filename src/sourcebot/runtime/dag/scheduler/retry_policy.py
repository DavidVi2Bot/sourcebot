# sourcebot/runtime/dag/scheduler/retry_policy.py
import random
class RetryPolicy:

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: int = 2,
        max_delay: int = 30,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_attempts

    def get_delay(self, attempt: int) -> float:

        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay