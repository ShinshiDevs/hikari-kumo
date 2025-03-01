from __future__ import annotations

from collections.abc import Generator, Sequence
from logging import Logger, getLogger
from typing import TYPE_CHECKING

from hikari import api
from hikari.commands import CommandChoice, CommandOption, CommandType, OptionType
from hikari.traits import RESTAware

from kumo.commands.base import Command, CommandGroup, SubCommand
from kumo.commands.metadata import MessageCommandMetadata, SlashCommandMetadata, SubCommandMetadata, UserCommandMetadata
from kumo.commands.options import Choice, Option
from kumo.i18n.abc import ILocalizationProvider

if TYPE_CHECKING:
    from kumo.commands.types import CommandT

__all__: Sequence[str] = ()

_LOGGER: Logger = getLogger("kumo.commands.builder")


class CommandBuilder:
    __slots__: Sequence[str] = ("__logger", "bot", "i18n", "commands")

    def __init__(self, bot: RESTAware, i18n: ILocalizationProvider) -> None:
        self.bot: RESTAware = bot
        self.i18n: ILocalizationProvider = i18n

    def build_choice(self, choice: Choice) -> CommandChoice:
        return CommandChoice(name=choice.name, value=choice.value)

    def build_option(self, option: Option) -> CommandOption:
        return CommandOption(
            type=option.type,
            name=option.name,
            description=option.description,
            is_required=option.is_required,
            min_value=option.min_value,
            max_value=option.max_value,
            min_length=option.min_length,
            max_length=option.max_length,
            channel_types=option.channel_types,
        )

    def build_command(self, command: Command) -> api.CommandBuilder:
        match command.metadata:
            case SlashCommandMetadata():
                builder: api.SlashCommandBuilder = (
                    self.bot.rest.slash_command_builder(command.metadata.name, command.metadata.description)
                    .set_default_member_permissions(command.metadata.default_member_permissions)
                    .set_is_dm_enabled(command.metadata.is_dm_enabled)
                    .set_is_nsfw(command.metadata.is_nsfw)
                )
                for option in command.metadata.options:
                    builder.add_option(self.build_option(option))
                return builder
            case UserCommandMetadata():
                return self.bot.rest.context_menu_command_builder(CommandType.USER, command.metadata.name)
            case MessageCommandMetadata():
                return self.bot.rest.context_menu_command_builder(CommandType.MESSAGE, command.metadata.name)
            case _:
                raise Exception()  # TODO(exceptions): invalid metadata

    def build_commands(self, commands: Sequence[CommandT]) -> Generator[api.CommandBuilder]:
        for command in commands:
            if isinstance(command, Command):
                yield self.build_command(command)
            else:
                yield self.build_command_group(command)

    def build_sub_command(self, metadata: SubCommandMetadata) -> CommandOption:
        return CommandOption(
            type=OptionType.SUB_COMMAND,
            name=metadata.name,
            description=metadata.description,
            options=[self.build_option(option) for option in metadata.options],
        )

    def build_command_group(self, group: CommandGroup) -> api.SlashCommandBuilder:
        assert isinstance(group.metadata, SlashCommandMetadata)
        builder: api.SlashCommandBuilder = (
            self.bot.rest.slash_command_builder(group.metadata.name, "-")
            .set_default_member_permissions(group.metadata.default_member_permissions)
            .set_is_dm_enabled(group.metadata.is_dm_enabled)
            .set_is_nsfw(group.metadata.is_nsfw)
        )
        for command in group.commands.values():
            if isinstance(command, SubCommand):
                builder.add_option(self.build_sub_command(command.metadata))
            else:
                builder.add_option(
                    CommandOption(
                        type=OptionType.SUB_COMMAND_GROUP,
                        name=command.metadata.name,
                        description="-",
                        options=[self.build_sub_command(sub_command.metadata) for sub_command in command.commands],
                    )
                )

        return builder
