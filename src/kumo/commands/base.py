from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Sequence
from types import MethodType
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from kumo.commands.exceptions import CommandNotFoundException
from kumo.commands.utils import get_callback

if TYPE_CHECKING:
    from kumo.commands.metadata import CommandMetadata, SlashCommandMetadata, SubCommandMetadata
    from kumo.commands.types import CommandCallbackT

__all__: Sequence[str] = ("Command", "SubCommand", "SubCommandGroup", "CommandGroup")

Item = TypeVar("Item")


class Command:
    __slots__: Sequence[str] = ("obj", "callback", "metadata")

    def __init__(self, obj: type, metadata: CommandMetadata, *, callback: CommandCallbackT | None = None) -> None:
        self.obj: type = obj
        self.callback: CommandCallbackT = callback or get_callback(obj)
        self.metadata: CommandMetadata = metadata

    def get_callback(self) -> CommandCallbackT:
        return MethodType(self.obj, self.callback) if inspect.isclass(self.obj) else self.callback  # TODO: something smarter


class SubCommand:  # noqa: B903
    __slots__: Sequence[str] = ("group", "callback", "metadata")

    def __init__(
        self, callback: CommandCallbackT, metadata: SubCommandMetadata, *, group: SubCommandGroup | None = None
    ) -> None:
        self.group: SubCommandGroup | None = group
        self.callback: CommandCallbackT = callback
        self.metadata: SubCommandMetadata = metadata


class Group(ABC, Generic[Item]):
    __slots__: Sequence[str] = ("metadata", "commands")

    def __init__(self, metadata: SlashCommandMetadata | SubCommandMetadata) -> None:
        self.metadata: SlashCommandMetadata | SubCommandMetadata = metadata
        self.commands: dict[Any, Item] = {}  # type: ignore

    @abstractmethod
    def add_command(self, command: Item) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_command(self, name: str) -> Item:
        raise NotImplementedError


class SubCommandGroup(Group[SubCommand]):
    def __init__(self, metadata: SubCommandMetadata) -> None:
        super().__init__(metadata)

    def add_command(self, command: SubCommand) -> None:
        self.commands[command.metadata.name] = command

    def get_command(self, name: str) -> SubCommand:
        return self.commands[name]


class CommandGroup(Group[SubCommand | SubCommandGroup]):
    def __init__(self, obj: type, metadata: SlashCommandMetadata) -> None:
        self.obj: type = obj
        super().__init__(metadata)

    def add_command(self, command: SubCommand | SubCommandGroup) -> None:
        self.commands[command.metadata.name] = command

    def get_command(self, name: str, *, group: str | None = None) -> SubCommand:
        command_group: CommandGroup | SubCommandGroup = self
        if group is not None:
            if sub_group := self.commands.get(group):
                assert isinstance(sub_group, SubCommandGroup)
                command_group = sub_group
            else:
                raise CommandNotFoundException(f"Cannot get sub command group {group} in {self.metadata.name}")
            if command := command_group.commands.get(name):
                return command
            raise CommandNotFoundException(f"Cannot get {self.metadata.name} {group} {name}")
        if command := command_group.commands.get(name):
            return command
        raise CommandNotFoundException(f"Cannot get {self.metadata.name} {name}")
