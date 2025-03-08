from __future__ import annotations

import inspect
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from hikari.commands import OptionType

if TYPE_CHECKING:
    from hikari.guilds import Role
    from hikari.interactions import (
        CommandInteraction,
        CommandInteractionOption,
        InteractionChannel,
        InteractionMember,
        ResolvedOptionData,
    )
    from hikari.messages import Attachment
    from hikari.snowflakes import Snowflake
    from hikari.users import User

    from kumo.commands.types import CommandCallbackT

__all__: Sequence[str] = ("get_callback",)

ArgumentT = (
    InteractionMember | User | InteractionChannel | Role | Attachment | Snowflake | str | int | float | bool | None
)


def get_callback(obj: object) -> CommandCallbackT:
    if inspect.isclass(obj):
        for attr in obj.__dict__.values():
            if inspect.iscoroutinefunction(attr):
                return attr
    elif inspect.iscoroutinefunction(obj):
        return obj
    raise Exception()  # TODO(exceptions): invalid callback


def unpack_resolved_data(resolved_data: ResolvedOptionData) -> Mapping[str, Any]:
    return {key: value for key, value in vars(resolved_data).items() if value}


def resolve_argument(interaction: CommandInteraction, option: CommandInteractionOption) -> ArgumentT:
    if not interaction.resolved or not isinstance(option.value, Snowflake):
        return option.value
    value = Snowflake(option.value)
    match option.type:
        case OptionType.USER:
            return interaction.resolved.members.get(value, interaction.resolved.users.get(value))
        case OptionType.CHANNEL:
            return interaction.resolved.channels.get(value)
        case OptionType.ROLE:
            return interaction.resolved.roles.get(value)
        case OptionType.MENTIONABLE:
            return interaction.resolved.members.get(value, interaction.resolved.roles.get(value))
        case OptionType.ATTACHMENT:
            return interaction.resolved.attachments.get(value)
        case _:
            return None
