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
