from __future__ import annotations

from collections.abc import Callable, Coroutine, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kumo.commands.base import Command, CommandGroup

    CommandT = Command | CommandGroup

__all__: Sequence[str] = ("CommandCallbackT", "CommandT")

CommandCallbackT = Callable[..., Coroutine[Any, Any, None]]
