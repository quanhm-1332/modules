import asyncio

from sunbot.std import run_sync


def test_run_sync_runs_blocking_callable() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    assert asyncio.run(run_sync(add, 2, 3)) == 5
