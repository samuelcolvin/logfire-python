from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List, Tuple, Any, Dict, Optional

__all__ = ('LogLevels', 'Record')


class LogLevels(IntEnum):
    debug = 10
    info = 20
    notice = 25
    warning = 30
    error = 40
    critical = 50


@dataclass
class Record:
    ts: datetime
    level: LogLevels
    template: str
    message: str
    stack: List[Tuple[str, int]]
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    exc: Optional[Exception] = None
