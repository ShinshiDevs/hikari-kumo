from __future__ import annotations

from collections.abc import Sequence

import attrs

from kumo.context import CommandInteractionContext
from kumo.events.interaction_events import InteractionExceptionEvent

__all__: Sequence[str] = ("CommandCallbackErrorEvent",)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class CommandCallbackErrorEvent(InteractionExceptionEvent[CommandInteractionContext]): ...
