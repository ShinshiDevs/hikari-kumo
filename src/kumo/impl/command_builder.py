from __future__ import annotations

from collections.abc import Generator, Mapping, Sequence
from logging import getLogger
from typing import TYPE_CHECKING

from hikari import api
from hikari.commands import CommandChoice, CommandOption, CommandType, OptionType

from kumo.commands.metadata import MessageCommandMetadata, SlashCommandMetadata, SubCommandMetadata, UserCommandMetadata
from kumo.commands.options import Choice, Option
from kumo.i18n.types import Localized
from kumo.internal.consts import DEFAULT_DESCRIPTION, GROUP_DESCRIPTION

if TYPE_CHECKING:
    from hikari.locales import Locale
    from hikari.traits import RESTAware

    from kumo.commands.base import Command, CommandGroup, SubCommand, SubCommandGroup
    from kumo.commands.types import CommandT
    from kumo.i18n.abc import ILocalizationProvider

__all__: Sequence[str] = ()

_LOGGER = getLogger("kumo.commands.builder")


class CommandBuilder:
    __slots__: Sequence[str] = ("__logger", "bot", "i18n", "commands")

    def __init__(self, bot: RESTAware, *, i18n: ILocalizationProvider | None = None) -> None:
        self.bot = bot
        self.i18n: ILocalizationProvider | None = i18n

    def build_localized(self, localized: Localized) -> tuple[Mapping[Locale | str, str], str]:
        if not self.i18n:
            _LOGGER.warning("localized object %s cannot be builded without localization provider", localized.key)
            return {}, localized.key
        return self.i18n.localize(localized)

    def build_choice(self, choice: Choice) -> CommandChoice:
        return CommandChoice(
            name=choice.name,
            value=choice.value,
            name_localizations=self.build_localized(choice.display_name)[0] if choice.display_name else {},
        )

    def build_option(self, option: Option) -> CommandOption:
        if isinstance(option.description, Localized):
            description_localizations, description = self.build_localized(option.description)
        else:
            description_localizations, description = {}, option.description
        return CommandOption(
            type=option.type,
            name=option.name,
            description=description or DEFAULT_DESCRIPTION,
            choices=[self.build_choice(choice) for choice in option.choices] if option.choices else None,
            is_required=option.is_required,
            min_value=option.min_value,
            max_value=option.max_value,
            min_length=option.min_length,
            max_length=option.max_length,
            channel_types=option.channel_types,
            name_localizations=self.build_localized(option.display_name)[0] if option.display_name else {},
            description_localizations=description_localizations,  # type: ignore
        )

    def build_command(self, command: Command) -> api.CommandBuilder:
        match command.metadata:
            case SlashCommandMetadata():
                if isinstance(command.metadata.description, Localized):
                    description_localizations, description = self.build_localized(command.metadata.description)
                else:
                    description_localizations, description = {}, command.metadata.description
                builder = (
                    self.bot.rest.slash_command_builder(command.metadata.name, description or DEFAULT_DESCRIPTION)
                    .set_description_localizations(description_localizations)  # type: ignore
                )
                for option in command.metadata.options or ():
                    builder.add_option(self.build_option(option))
            case UserCommandMetadata():
                builder = self.bot.rest.context_menu_command_builder(
                    CommandType.USER, command.metadata.name
                )
            case MessageCommandMetadata():
                builder = self.bot.rest.context_menu_command_builder(
                    CommandType.MESSAGE, command.metadata.name
                )
            case _:
                raise Exception()  # TODO(exceptions): invalid metadata

        if command.metadata.display_name:
            localizations, _ = self.build_localized(command.metadata.display_name)
            builder.set_name_localizations(localizations)

        builder.set_default_member_permissions(command.metadata.default_member_permissions)
        builder.set_is_dm_enabled(command.metadata.is_dm_enabled)
        builder.set_is_nsfw(command.metadata.is_nsfw)

        return builder

    def build_commands(self, commands: Sequence[CommandT]) -> Generator[api.CommandBuilder]:
        for command in commands:
            if isinstance(command, Command):
                yield self.build_command(command)
            else:
                yield self.build_command_group(command)

    def build_sub_command(self, metadata: SubCommandMetadata) -> CommandOption:
        if isinstance(metadata.description, Localized):
            description_localizations, description = self.build_localized(metadata.description)
        else:
            description_localizations, description = {}, metadata.description
        return CommandOption(
            type=OptionType.SUB_COMMAND,
            name=metadata.name,
            description=description or DEFAULT_DESCRIPTION,
            options=[self.build_option(option) for option in metadata.options] if metadata.options else None,
            description_localizations=description_localizations,  # type: ignore
            name_localizations=self.build_localized(metadata.display_name)[0] if metadata.display_name else {},
        )

    def build_sub_command_group(self, group: SubCommandGroup) -> CommandOption:
        return CommandOption(
            type=OptionType.SUB_COMMAND_GROUP,
            name=group.metadata.name,
            description=GROUP_DESCRIPTION,
            options=[self.build_sub_command(sub_command.metadata) for sub_command in group.commands],
            name_localizations=self.build_localized(group.metadata.display_name)[0] if group.metadata.display_name else {},
        )

    def build_command_group(self, group: CommandGroup) -> api.SlashCommandBuilder:
        assert isinstance(group.metadata, SlashCommandMetadata)
        builder: api.SlashCommandBuilder = (
            self.bot.rest.slash_command_builder(group.metadata.name, GROUP_DESCRIPTION)
            .set_default_member_permissions(group.metadata.default_member_permissions)
            .set_is_dm_enabled(group.metadata.is_dm_enabled)
            .set_is_nsfw(group.metadata.is_nsfw)
        )
        if group.metadata.display_name:
            localizations, _ = self.build_localized(group.metadata.display_name)
            builder.set_name_localizations(localizations)

        for command in group.commands.values():
            if isinstance(command, SubCommand):
                builder.add_option(self.build_sub_command(command.metadata))
            else:
                builder.add_option(
                    self.build_sub_command_group(command)
                )

        return builder
