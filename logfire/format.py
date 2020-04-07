import re
from typing import Tuple, Any, Optional, Dict


def format_message(template: str, args: Tuple[Any, ...], kwargs: Dict[str, Any], exc: Optional[BaseException]):
    format_kwargs = dict(kwargs)
    if '_args_' not in format_kwargs:
        format_kwargs['_args_'] = RenderArgs(args, kwargs, exc)

    return re.sub('=$', '{_args_}', template).format(*args, **format_kwargs)


class RenderArgs:
    __slots__ = 'args', 'kwargs', 'exc'

    def __init__(self, args: Tuple[Any, ...], kwargs: Dict[str, Any], exc: Optional[BaseException]):
        self.args = args
        self.kwargs = kwargs
        self.exc = exc

    def __format__(self, format_spec) -> str:
        # TODO
        return str(self)

    def __str__(self) -> str:
        parts = [repr(a) for a in self.args] + ['{}={!r}'.format(*kv) for kv in self.kwargs.items()]
        if self.exc:
            parts.append('{}: {}'.format(self.exc.__class__.__name__, self.exc))
        return ' '.join(parts)
