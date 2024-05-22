"""
ThreadPoolService provides abstraction layer to submit synchronous tasks
to asynchronous using thread pool.
"""

from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Awaitable, Any
from concurrent.futures import ThreadPoolExecutor
from asyncio.events import AbstractEventLoop
import asyncio

R = TypeVar("R")

class ThreadPoolService(ABC):
    """
    ThreadPoolService provides a way to run synchronous tasks in a separate
    thread and awaiting for their result asynchronously.
    """

    @abstractmethod
    def run_in_thread(
        self, func: Callable[[Any, ...], R], *args: Any, **kwargs: Any
    ) -> Awaitable[R]:
        """
        Runs the provided callable in separate thread and returns an awaitable.
        """

    def shutdown(self) -> None:
        """Shuts down the thread pool."""


async def get_thread_pool_service() -> ThreadPoolService:
    """Dependency factory to create instance of ThreadPoolService."""
    loop = asyncio.get_event_loop()
    return AioThreadPoolService(loop, 8)


class AioThreadPoolService(ThreadPoolService):
    """
    ThreadPoolService provides a way to run synchronous tasks in a separate
    thread and awaiting for their result asynchronously.
    """

    def __init__(self, loop: AbstractEventLoop, max_workers: int) -> None:
        self._pool = ThreadPoolExecutor(max_workers)
        self._loop = loop

    def run_in_thread(
        self, func: Callable[[Any, ...], R], *args: Any, **kwargs: Any
    ) -> Awaitable[R]:
        return self._loop.run_in_executor(self._pool, func, *args, **kwargs)

    def shutdown(self) -> None:
        self._pool.shutdown(wait=True, cancel_futures=True)
