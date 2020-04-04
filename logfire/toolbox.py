import inspect
import re
from typing import List, Tuple

this_package = re.compile(r'/logfire/[a-z_]+\.py$')


def get_stack() -> List[Tuple[str, int]]:
    external_frames: List[Tuple[str, int]] = []
    for f in inspect.getouterframes(inspect.currentframe(), context=0):
        if not this_package.search(f.filename):
            external_frames.append((f.filename, f.lineno))

    return external_frames
