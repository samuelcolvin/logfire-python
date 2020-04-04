import sys
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from .send import ThreadSender
from .toolbox import get_stack
from .record import LogLevels, Record

__all__ = ('LogClient',)


class LogClient:
    def __init__(self):
        self._level = LogLevels.info
        self._sender = None

    def set(self, log_level: LogLevels):
        self._level = log_level

    def log(self, level: LogLevels, template: str, *args: Any, **kwargs: Any):
        if self._level >= level:
            self._log(level, template, *args, **kwargs)

    def debug(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.debug:
            self._log(LogLevels.debug, template, *args, **kwargs)

    def info(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.info:
            self._log(LogLevels.info, template, *args, **kwargs)

    def notice(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.notice:
            self._log(LogLevels.notice, template, *args, **kwargs)

    def warning(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.warning:
            self._log(LogLevels.warning, template, *args, **kwargs)

    def error(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.error:
            self._log(LogLevels.error, template, *args, **kwargs)

    def critical(self, template: str, *args: Any, **kwargs: Any):
        if self._level >= LogLevels.critical:
            self._log(LogLevels.critical, template, *args, **kwargs)

    def _log(self, level: LogLevels, template: str, *args, **kwargs: Any):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        record = Record(
            ts=self._now(),
            level=level,
            template=template,
            message=template.format(*args, **kwargs),
            stack=get_stack(),
            args=args,
            kwargs=kwargs,
        )
        self._print(record)
        self._send(record)

    @staticmethod
    def _print(r: Record):
        print(f'{r.ts:%H:%M:%S}.{r.ts.microsecond / 1000::<3d} | {r.message}', file=sys.stderr, flush=True)

    def _send(self, r: Record):
        if self.sender is None:
            self.sender = ThreadSender()
        self.sender.put(r)

    @staticmethod
    def _now():
        """
        Now in the local timezone
        """
        return datetime.now(timezone.utc).astimezone()
