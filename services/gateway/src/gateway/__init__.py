from collections.abc import Awaitable, Callable
from typing import Literal

type ASGIApp = Callable[..., Awaitable[None]]


def build_litestar() -> ASGIApp:
    from litestar import Litestar, get

    @get("/")
    async def root() -> str:
        return "hello"

    app = Litestar([root])
    return app


def build_fastapi() -> ASGIApp:
    from fastapi import FastAPI

    async def root() -> str:
        return "hello"

    app = FastAPI()

    app.get("/")(root)

    return app


def _run_app(
    server: Literal["uvicorn", "granian"] = "uvicorn",
    asgi_app: Literal["fastapi", "litestar"] = "fastapi",
):
    match asgi_app:
        case "fastapi":
            _app = build_fastapi()
        case "litestar":
            _app = build_litestar()
    match server:
        case "granian":
            import asyncio

            from granian.server.embed import Server

            _server = Server(_app)
            asyncio.run(_server.serve())
        case "uvicorn":
            from uvicorn import run

            run(_app)


def main() -> None:
    print("Hello from gateway!")
    _run_app()
