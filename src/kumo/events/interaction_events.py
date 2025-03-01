from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

import attrs
from hikari.interactions.base_interactions import PartialInteraction
from hikari.traits import RESTAware

from kumo.events.base_events import Event, ExceptionEvent

__all__: Sequence[str] = ("InteractionEvent", "InteractionExceptionEvent")

T = TypeVar("T", bound=PartialInteraction)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class InteractionEvent(Event, Generic[T]):
    interaction: T = attrs.field()

    @property
    def app(self) -> RESTAware:
        return self.interaction.app


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class InteractionExceptionEvent(InteractionEvent[T], ExceptionEvent, Generic[T]): ...
