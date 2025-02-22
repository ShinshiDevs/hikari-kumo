from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

import attrs
from hikari.interactions import CommandInteraction, PartialInteraction

__all__: Sequence[str] = ("CommandInteractionContext",)

T = TypeVar("T", bound=PartialInteraction)


@attrs.define(kw_only=True, slots=True)
class InteractionContext(Generic[T]):
    interaction: T


@attrs.define(kw_only=True, slots=True)
class CommandInteractionContext(InteractionContext[CommandInteraction]): ...
