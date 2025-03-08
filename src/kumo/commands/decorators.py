from __future__ import annotations

import inspect
from collections.abc import Callable, Generator, Sequence
from typing import TYPE_CHECKING

from hikari import UNDEFINED

from kumo.commands.base import Command, CommandGroup, SubCommand, SubCommandGroup
from kumo.commands.metadata import MessageCommandMetadata, SlashCommandMetadata, SubCommandMetadata, UserCommandMetadata
from kumo.commands.options import Option
from kumo.commands.utils import get_callback
from kumo.i18n.types import Localized, LocalizedOr
from kumo.internal.consts import DEFAULT_DESCRIPTION, GROUP_DESCRIPTION

if TYPE_CHECKING:
    from hikari.permissions import Permissions
    from hikari.undefined import UndefinedOr

    from kumo.commands.types import CommandCallbackT

__all__: Sequence[str] = ("user_command", "message_command", "slash_command", "command_group", "sub_command", "sub_command_group")


def get_sub_commands(obj: object) -> Generator[SubCommandGroup | SubCommand]:
    for attr in obj.__dict__.values():
        if isinstance(attr, SubCommand) and attr.group is None or isinstance(attr, SubCommandGroup):
            yield attr


def user_command(
    name: str,
    *,
    display_name: Localized | None = None,
    default_member_permissions: UndefinedOr[Permissions] = UNDEFINED,
    is_dm_enabled: UndefinedOr[bool] = UNDEFINED,
    is_nsfw: UndefinedOr[bool] = UNDEFINED,
) -> Callable[[type], Command]:
    def inner(obj: type) -> Command:
        return Command(
            obj=obj,
            metadata=UserCommandMetadata(
                name=name,
                display_name=display_name,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=is_dm_enabled,
                is_nsfw=is_nsfw,
            )
        )

    return inner


def message_command(
    name: str,
    *,
    display_name: Localized | None = None,
    default_member_permissions: UndefinedOr[Permissions] = UNDEFINED,
    is_dm_enabled: UndefinedOr[bool] = UNDEFINED,
    is_nsfw: UndefinedOr[bool] = UNDEFINED,
) -> Callable[[type], Command]:
    def inner(obj: type) -> Command:
        return Command(
            obj=obj,
            metadata=MessageCommandMetadata(
                name=name,
                display_name=display_name,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=is_dm_enabled,
                is_nsfw=is_nsfw,
            )
        )

    return inner


def slash_command(
    name: str,
    *,
    display_name: Localized | None = None,
    description: LocalizedOr[str] = DEFAULT_DESCRIPTION,
    options: Sequence[Option] | None = None,
    default_member_permissions: UndefinedOr[Permissions] = UNDEFINED,
    is_dm_enabled: UndefinedOr[bool] = UNDEFINED,
    is_nsfw: UndefinedOr[bool] = UNDEFINED,
) -> Callable[[type], Command]:
    def inner(obj: type) -> Command:
        callback: CommandCallbackT = get_callback(obj)
        # TODO: get options from callback signature
        return Command(
            obj=obj,
            callback=callback,
            metadata=SlashCommandMetadata(
                name=name,
                display_name=display_name,
                description=description,
                options=options,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=is_dm_enabled,
                is_nsfw=is_nsfw,
            )
        )

    return inner


def sub_command(
    name: str,
    *,
    display_name: Localized | None = None,
    description: LocalizedOr[str] = DEFAULT_DESCRIPTION,
    options: Sequence[Option] | None = None,
) -> Callable[[CommandCallbackT], SubCommand]:
    def inner(callback: CommandCallbackT) -> SubCommand:
        # TODO: get options from callback signature
        return SubCommand(
            callback=callback,
            metadata=SubCommandMetadata(
                name=name,
                display_name=display_name,
                description=description,
                options=options,
            )
        )

    return inner


def command_group(
    name: str,
    *,
    display_name: Localized | None = None,
    default_member_permissions: UndefinedOr[Permissions] = UNDEFINED,
    is_dm_enabled: UndefinedOr[bool] = UNDEFINED,
    is_nsfw: UndefinedOr[bool] = UNDEFINED,
) -> Callable[[type], CommandGroup]:
    def inner(obj: type) -> CommandGroup:
        group: CommandGroup = CommandGroup(
            obj=obj,
            metadata=SlashCommandMetadata(
                name=name,
                display_name=display_name,
                description=GROUP_DESCRIPTION,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=is_dm_enabled,
                is_nsfw=is_nsfw,
            )
        )
        if inspect.isclass(obj):
            for command in get_sub_commands(obj):
                group.add_command(command)
        return group

    return inner


def sub_command_group(
    name: str,
    *,
    display_name: Localized | None = None,
) -> Callable[[type], SubCommandGroup]:
    def inner(obj: type) -> SubCommandGroup:
        return SubCommandGroup(
            metadata=SubCommandMetadata(
                name=name,
                display_name=display_name,
                description=GROUP_DESCRIPTION,
            )
        )

    return inner
