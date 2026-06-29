"""Utilities, Runtime-specific (asyncio event loop, threading/ThreadPool, multiprocessing/ProcessPool) logic
Low-priority:
Concurrency control: RateLimit, Semaphore (max_concurrency) -> Logic + Interface + decorator
"""

import asyncio
from collections.abc import Callable


async def run_sync[T, **P](
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """Run a blocking sync callable in the default executor off the event loop."""
    loop = asyncio.get_running_loop()

    def _wrapper() -> T:
        return func(*args, **kwargs)

    return await loop.run_in_executor(None, _wrapper)
