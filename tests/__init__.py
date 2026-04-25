"""Test helpers — importable by all test files."""

import inspect
from typing import TypeVar, Callable, Any
from collections.abc import AsyncGenerator, Generator

T = TypeVar("T")


async def run_event(handler: Callable[..., T], *args, **kwargs) -> T:
    """Call a Reflex event handler, handling all variants (sync/async/generator).

    Usage::

        from tests import run_event

        await run_event(state.increment)
        await run_event(state.set_name, "Alice")
    """
    result = handler(*args, **kwargs)
    if inspect.iscoroutine(result):
        return await result
    if isinstance(result, AsyncGenerator):
        last: T | None = None
        async for chunk in result:
            last = chunk
        return last
    if isinstance(result, Generator):
        last: T | None = None
        for chunk in result:
            last = chunk
        return last
    return result
