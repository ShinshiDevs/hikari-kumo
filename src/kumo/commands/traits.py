from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar

from hikari.api import CommandBuilder

from kumo.context import CommandInteractionContext
from kumo.traits import BotAware

__all__: Sequence[str] = ("BuilderAware", "CallbackAware")

CommandBuilderT = TypeVar("CommandBuilderT", bound=CommandBuilder, covariant=True)


class BuilderAware(Protocol, Generic[CommandBuilderT]):
    @abstractmethod
    def builder(self, bot: BotAware) -> CommandBuilderT:
        raise NotImplementedError


class CallbackAware(Protocol):
    @abstractmethod
    async def callback(self, context: CommandInteractionContext) -> None:
        raise NotImplementedError
