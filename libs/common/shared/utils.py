import asyncio
from asyncio import AbstractEventLoop


__all__ = ("get_or_create_event_loop",)


def get_or_create_event_loop() -> AbstractEventLoop:
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
