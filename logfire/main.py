import json
import sys
from datetime import datetime, timezone
from typing import Any, Union, TYPE_CHECKING

from .format import format_message
from .record import LogLevels, Record, get_stack
from .send import ThreadSender
from .serialize import json_encoder

__all__ = ('LogClient',)

if TYPE_CHECKING:
    ExcType = Union[bool, BaseException]

DFT_TEMPLATE = '{_args_}'


class LogClient:
    def __init__(self):
        self._level = LogLevels.info
        self._sender = None

    def set(self, log_level: LogLevels):
        self._level = log_level

    def log(self, level: LogLevels, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = False, **kwargs: Any):
        if self._level <= level:
            self._log(level, template, *args, exc_=exc_, **kwargs)

    def debug(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = False, **kwargs: Any):
        if self._level <= LogLevels.debug:
            self._log(LogLevels.debug, template, *args, exc_=exc_, **kwargs)

    def info(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = False, **kwargs: Any):
        if self._level <= LogLevels.info:
            self._log(LogLevels.info, template, *args, exc_=exc_, **kwargs)

    def notice(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = False, **kwargs: Any):
        if self._level <= LogLevels.notice:
            self._log(LogLevels.notice, template, *args, exc_=exc_, **kwargs)

    def warning(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = True, **kwargs: Any):
        if self._level <= LogLevels.warning:
            self._log(LogLevels.warning, template, *args, exc_=exc_, **kwargs)

    def error(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = True, **kwargs: Any):
        if self._level <= LogLevels.error:
            self._log(LogLevels.error, template, *args, exc_=exc_, **kwargs)

    def critical(self, template: str = DFT_TEMPLATE, *args: Any, exc_: 'ExcType' = True, **kwargs: Any):
        self._log(LogLevels.critical, template, *args, exc_=exc_, **kwargs)

    def _log(self, level: LogLevels, template: str = DFT_TEMPLATE, *args, exc_: 'ExcType' = False, **kwargs: Any):
        timestamp = self._now()
        exc = None
        if exc_ is True:
            exc = sys.exc_info()[1]
        elif isinstance(exc_, BaseException):
            exc = exc_
        elif exc_ not in {False, None}:
            # TODO warning or error
            raise TypeError('exc_ should be either a bool or an exception instance')

        record = Record(
            timestamp=timestamp,
            level=level,
            template=template,
            message=format_message(template, args, kwargs, exc),
            stack=get_stack(),
            args=args,
            kwargs=kwargs,
            exc=exc,
        )
        self._print(record)
        self._send(record)

    @staticmethod
    def _print(r: Record):
        ts = r.timestamp
        print(f'{ts:%H:%M:%S}.{ts.microsecond // 1000:<3d}    {r.message}', file=sys.stderr, flush=True)

    def _send(self, r: Record):
        if self._sender is None:
            self._sender = ThreadSender()
        data = dict(
            timestamp=r.timestamp,
            level=r.level,
            message=r.message,
            stack=[(f.filename, f.lineno) for f in r.stack],
        )
        if r.args:
            data['args'] = r.args
        if r.kwargs:
            data['kwargs'] = r.kwargs
        if r.exc:
            data['exc'] = {'type': r.exc.__class__.__name__, 'value': str(r.exc)}

        s = json.dumps(data, default=json_encoder)
        self._sender.put(s)

    @staticmethod
    def _now():
        """
        Now in the local timezone
        """
        return datetime.now(timezone.utc).astimezone()
