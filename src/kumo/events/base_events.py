from __future__ import annotations

import types
from collections.abc import Sequence

import attrs
from hikari.events.base_events import Event as hikari_Event

from kumo.traits import BotAware

__all__: Sequence[str] = ("Event", "ExceptionEvent")


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class Event(hikari_Event):
    bot: BotAware = attrs.field()


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class ExceptionEvent(Event):
    exception: Exception = attrs.field()

    @property
    def exc_info(self) -> tuple[type[Exception], Exception, types.TracebackType | None]:
        return type(self.exception), self.exception, self.exception.__traceback__
