import inspect
import re
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List, Tuple, Any, Dict, Optional

__all__ = 'LogLevels', 'Record', 'get_stack'


class LogLevels(IntEnum):
    debug = 10
    info = 20
    notice = 25
    warning = 30
    error = 40
    critical = 50


@dataclass
class Frame:
    filename: str
    lineno: int
    function: str
    code_context: str


@dataclass
class Record:
    timestamp: datetime
    level: LogLevels
    template: str
    message: str
    stack: List[Frame]
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    exc: Optional[BaseException] = None


def get_stack() -> List[Frame]:
    external_frames: List[Frame] = []
    for f in inspect.getouterframes(inspect.currentframe(), context=0):
        if not re.search(r'/logfire/[a-z_]+\.py$', f.filename):
            external_frames.append(Frame(
                filename=f.filename,
                lineno=f.lineno,
                function=f.function,
                code_context=f.code_context,
            ))

    return external_frames
