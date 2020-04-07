import datetime
from dataclasses import asdict, is_dataclass
from types import GeneratorType
from typing import Any, Callable, Dict, Type, Union

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None

__all__ = ('json_encoder',)


def datetime_isoformat(o: Union[datetime.date, datetime.time]) -> str:
    # TODO, I think this needs fixing to match postgres etc.
    return o.isoformat()


def pydantic_model_to_dict(m: 'BaseModel') -> Dict[str, Any]:
    return m.dict()


ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    datetime.datetime: datetime_isoformat,
    datetime.date: datetime_isoformat,
    set: list,
    frozenset: list,
    GeneratorType: list,
}
if BaseModel is not None:
    ENCODERS_BY_TYPE[BaseModel] = pydantic_model_to_dict


def json_encoder(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)

    # Check the class type and its superclasses for a matching encoder
    for base in obj.__class__.__mro__[:-1]:
        try:
            encoder = ENCODERS_BY_TYPE[base]
        except KeyError:
            continue
        return encoder(obj)
    else:  # We have exited the for loop without finding a suitable encoder
        return repr(obj)
