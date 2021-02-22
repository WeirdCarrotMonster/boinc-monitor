import asyncio
from typing import Set, Awaitable, Iterable
from contextlib import contextmanager, suppress
import logging


LOGGER = logging.getLogger(__name__)


class ListenerPool:
    def __init__(self, loaders: Iterable[Awaitable], sleep_time: int = 1):
        self.has_listeners = asyncio.Event()
        self.stopped = asyncio.Event()

        self.listener_queue: Set[asyncio.Queue] = set()
        self.loaders = loaders
        self.sleep_time = sleep_time

    @contextmanager
    def listen_queue(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=5)
        self.listener_queue.add(queue)

        try:
            self.has_listeners.set()
            LOGGER.debug(
                "Adding event listener, total count %s", len(self.listener_queue)
            )
            yield queue
        finally:
            self.listener_queue.remove(queue)
            LOGGER.debug(
                "Removing event listener, total count %s", len(self.listener_queue)
            )
            if not self.listener_queue:
                self.has_listeners.clear()

    async def run_loop_for(self, loader: Awaitable):
        while not self.stopped.is_set():
            stopped = asyncio.create_task(self.stopped.wait())
            has_listeners = asyncio.create_task(self.has_listeners.wait())

            done, pending = await asyncio.wait(
                (stopped, has_listeners), return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            for task in done:
                task.result()

            if stopped in done:
                break

            try:
                result = await loader()

                for queue in self.listener_queue:
                    with suppress(asyncio.QueueFull):
                        queue.put_nowait(result)
            except GeneratorExit:
                raise
            except Exception:
                LOGGER.exception("Failed to get loader data")

            await asyncio.sleep(self.sleep_time)

    def start(self, *args, **kwargs):
        self.stopped.clear()

        for loader in self.loaders:
            asyncio.create_task(self.run_loop_for(loader))

    def stop(self, *args, **kwargs):
        self.stopped.set()
