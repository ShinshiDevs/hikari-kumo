from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

import attrs
from hikari.events import Event
from hikari.interactions import PartialInteraction
from hikari.traits import RESTAware

from kumo.context import InteractionContext
from kumo.events.base_events import ExceptionEvent

__all__: Sequence[str] = ("InteractionEvent", "InteractionExceptionEvent")

T = TypeVar("T", bound=InteractionContext[PartialInteraction])


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class InteractionEvent(Event, Generic[T]):
    context: T = attrs.field()

    @property
    def app(self) -> RESTAware:
        return self.context.interaction.app


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class InteractionExceptionEvent(InteractionEvent[T], ExceptionEvent, Generic[T]): ...
