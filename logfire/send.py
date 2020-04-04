import asyncio
import atexit
from queue import Queue
from datetime import datetime
from asyncio import CancelledError
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread, current_thread
from time import time

__all__ = ('ThreadSender',)


class ThreadSender:
    def __init__(self):
        self._queue = Queue()
        self._sender = Thread(target=self._run_thread, name='log_sender')
        self._sender.daemon = True
        self._sender.start()
        atexit.register(self.finish)

    def _run_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        send_records = ThreadSenderDaemon(self._queue)
        try:
            loop.run_until_complete(send_records.run())
        finally:
            loop.close()

    def put(self, record):
        self._queue.put(record)

    def finish(self):
        if self._queue:
            self._queue.put(finish)
            self._sender.join(timeout=5)
            self._queue = None


class Finish:
    pass


finish = Finish()


class ThreadSenderDaemon:
    def __init__(self, queue: Queue, *, send_interval: int = 1):
        self._queue = queue
        self._send_interval = send_interval
        self._records = []
        self.max_send = 10
        self._loop = asyncio.get_event_loop()

    async def run(self):
        send_task = self._loop.create_task(self._send_forever(), name='send')
        try:
            await self.collect_records()
        finally:
            try:
                send_task.cancel()
            except CancelledError:
                pass
            if self._records:
                await asyncio.shield(self._send())

    async def collect_records(self):
        with ThreadPoolExecutor(max_workers=1) as pool:
            while True:
                # TODO stop getting items from the queue until self._records "has space"
                log_record = await self._loop.run_in_executor(pool, self._queue.get)
                if log_record is finish:
                    return
                else:
                    self._queue.task_done()
                    self._records.append(log_record)

    async def _send_forever(self):
        """
        This attempts to constantly send records while throttling to send at a max rate of
        every self._send_interval seconds, this is not the same as debounce.
        """
        while True:
            if self._records:
                send_start = time()
                await asyncio.shield(self._send())
                sleep = max(self._send_interval - (time() - send_start), 0.1)
                await asyncio.sleep(sleep)
            else:
                await asyncio.sleep(0.01)

    async def _send(self):
        """
        Send self._records and clear
        """
        to_send = self._records[:]
        self._records = []
        n = datetime.now()
        print(f'{n:%H:%M:%S}.{n.microsecond / 1000:0.0f} sending {to_send} on "{current_thread().name}"...')
        await asyncio.sleep(1.2)
        n = datetime.now()
        print(f'{n:%H:%M:%S}.{n.microsecond / 1000:0.0f} sending {to_send} on "{current_thread().name}" done')
