import asyncio
import logging
from contextlib import contextmanager, suppress
from functools import partial
from typing import Awaitable, Iterable, Set

LOGGER = logging.getLogger(__name__)


class ListenerPool:
    def __init__(self, loaders: Iterable[Awaitable], sleep_time: int = 1):
        self.has_listeners = asyncio.Event()
        self.stopped = asyncio.Event()

        self.listener_queue: Set[asyncio.Queue] = set()
        self.loaders = loaders
        self.sleep_time = sleep_time

        self.loop_tasks = []

    def get_listen_queue(self) -> asyncio.Queue:
        client = PoolClient(maxsize=5)
        client.on_enter = partial(self.add_client, client=client)
        client.on_exit = partial(self.remove_client, client=client)
        return client

    def add_client(self, client: "PoolClient"):
        self.listener_queue.add(client)

        self.has_listeners.set()
        LOGGER.debug("Adding event listener, total count %s", len(self.listener_queue))

    def remove_client(self, client: "PoolClient"):
        self.listener_queue.remove(client)

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
            except Exception as e:
                LOGGER.exception("Failed to get loader data: %s", e)

            await asyncio.sleep(self.sleep_time)

    def start(self, *args, **kwargs):
        self.stopped.clear()

        for loader in self.loaders:
            loop_task = asyncio.create_task(self.run_loop_for(loader))
            self.loop_tasks.append(loop_task)

    async def stop(self, *args, **kwargs):
        self.stopped.set()

        await asyncio.gather(*self.loop_tasks)


class PoolClient(asyncio.Queue):

    on_enter = None
    on_exit = None

    def __enter__(self):
        self.on_enter()

    def __exit__(self, *args, **kwargs):
        self.on_exit()
