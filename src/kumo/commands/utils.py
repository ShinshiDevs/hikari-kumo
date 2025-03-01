from __future__ import annotations

import inspect
from collections.abc import Sequence

from kumo.commands.types import CommandCallbackT

__all__: Sequence[str] = ("get_callback",)


def get_callback(obj: object) -> CommandCallbackT:
    if inspect.isclass(obj):
        for attr in obj.__dict__.values():
            if inspect.iscoroutinefunction(attr):
                return attr
    elif inspect.iscoroutinefunction(obj):
        return obj
    raise Exception()  # TODO(exceptions): invalid callback
