from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine, Mapping, Sequence
from typing import Any, Generic, TypeVar

from hikari.api import CommandBuilder
from hikari.api.special_endpoints import SlashCommandBuilder

from kumo.commands.metadata import CommandMetadata, SlashCommandMetadata, SubCommandMetadata
from kumo.commands.traits import BuilderAware, CallbackAware
from kumo.commands.types import NameTuple
from kumo.context import CommandInteractionContext
from kumo.traits import BotAware

__all__: Sequence[str] = ("Command", "SubCommand", "CommandGroup")

T = TypeVar("T", bound=CommandBuilder)
Container = TypeVar("Container", bound=Mapping[Any, SubCommand] | None)
CommandCallbackT = Callable[..., Coroutine[Any, Any, None]]


class Command(ABC, CallbackAware, BuilderAware[T], Generic[T]):
    __slots__: Sequence[str] = ("_builder", "obj", "metadata")

    def __init__(self, obj: object, metadata: CommandMetadata) -> None:
        self._builder: T | None = None
        self.obj: object = obj
        self.metadata: CommandMetadata = metadata


class Group(ABC, Generic[Container]):
    __slots__: Sequence[str] = ("parent", "metadata", "commands")

    def __init__(self, metadata: SlashCommandMetadata | SubCommandMetadata, parent: Group[Any] | None = None) -> None:
        self.parent: Group[Any] | None = parent
        self.metadata: SlashCommandMetadata | SubCommandMetadata = metadata

        if self.parent is None:
            self.commands: Container = {}  # TODO: fix, if possible, or # type: ignore

    @abstractmethod
    def add_command(self, command: SubCommand) -> None:
        raise NotImplementedError


class SubCommand:
    __slots__: Sequence[str] = ("parent", "callback", "metadata")

    def __init__(
        self, callback: CommandCallbackT, metadata: SubCommandMetadata, *, parent: SubCommandGroup | None = None
    ) -> None:
        self.parent: SubCommandGroup | None = parent
        self.callback: CommandCallbackT = callback
        self.metadata: SubCommandMetadata = metadata


class SubCommandGroup(Group[None]):
    def __init__(self, parent: CommandGroup, metadata: SubCommandMetadata) -> None:
        super().__init__(metadata, parent)

    def add_command(self, command: SubCommand) -> None:
        assert self.parent
        return self.parent.add_command(command)


class CommandGroup(Group[dict[NameTuple, SubCommand]], BuilderAware[SlashCommandBuilder]):
    def __init__(self, obj: object, metadata: SlashCommandMetadata) -> None:
        super().__init__(metadata)

    def add_command(self, command: SubCommand) -> None:
        self.commands[
            (command.parent.metadata.name, command.metadata.name) if command.parent else (command.metadata.name,)
        ] = command

    def builder(self, bot: BotAware) -> SlashCommandBuilder: ...

    async def callback(self, context: CommandInteractionContext) -> None: ...
