from __future__ import annotations

import asyncio
from collections.abc import Sequence
from logging import getLogger
from typing import TYPE_CHECKING, Any

from hikari.commands import CommandType, OptionType
from hikari.events import InteractionCreateEvent
from hikari.interactions import CommandInteraction

from kumo.commands.base import Command
from kumo.commands.exceptions import CommandNotFoundException
from kumo.commands.utils import resolve_argument, unpack_resolved_data
from kumo.context import CommandInteractionContext
from kumo.events import CommandCallbackErrorEvent
from kumo.impl.command_builder import CommandBuilder

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop

    from hikari.snowflakes import Snowflake
    from hikari.traits import GatewayBotAware

    from kumo.commands.types import CommandCallbackT, CommandT
    from kumo.i18n.abc import ILocalizationProvider

__all__: Sequence[str] = ()

_LOGGER = getLogger("kumo.commands")


class CommandHandler:
    __slots__: Sequence[str] = ("_commands", "_loop", "bot", "i18n", "builder", "commands")

    def __init__(
        self, bot: GatewayBotAware, *, i18n: ILocalizationProvider | None = None, loop: AbstractEventLoop | None = None
    ) -> None:
        self._commands: dict[str, CommandT] = {}
        self._loop: AbstractEventLoop | None = loop

        self.bot = bot
        self.i18n: ILocalizationProvider | None = i18n
        self.builder = CommandBuilder(bot, i18n=i18n)

        self.commands: dict[Snowflake, CommandT] = {}

    @property
    def loop(self) -> AbstractEventLoop:
        if not self._loop:
            self._loop = asyncio.get_running_loop()
        return self._loop

    def create_context(self, interaction: CommandInteraction) -> CommandInteractionContext:
        return CommandInteractionContext(bot=self.bot, interaction=interaction, i18n=self.i18n)

    def add_command(self, command: CommandT) -> None:
        self._commands[command.metadata.name] = command
        _LOGGER.debug("add command %s", command.metadata.name)

    def get_command(self, command_id: Snowflake, *, command_name: str | None = None) -> CommandT:
        if command := self.commands.get(command_id):
            return command
        raise CommandNotFoundException(
            f"command with ID {command_id} is not found"
            if not command_name
            else f"command {command_name} (ID: {command_name}) is not found"
        )

    async def start(self, sync_commands: bool = True) -> None:
        _LOGGER.debug("starting, available commands: %s", len(self._commands))
        if sync_commands:
            await self.sync_commands()

    async def stop(self) -> None: ...  # TODO: clear commands

    async def dispatch(self, event: InteractionCreateEvent) -> None:
        assert isinstance(event.interaction, CommandInteraction)
        context = self.create_context(event.interaction)
        command = self.get_command(event.interaction.command_id)
        if isinstance(command, Command):
            if event.interaction.command_type in (CommandType.USER, CommandType.MESSAGE) and event.interaction.resolved:
                task = self._handle_callback(
                    command.get_callback(),
                    context,
                    *unpack_resolved_data(event.interaction.resolved),
                )
            else:
                task = self._handle_callback(
                    command.get_callback(),
                    context,
                    **{option.name: resolve_argument(event.interaction, option) for option in event.interaction.options},
                )
        else:
            if (option := event.interaction.options[0]).type is OptionType.SUB_COMMAND_GROUP:
                options = option.options or []
                options = options[0].options or []
                sub_command = command.get_command(option.name, group=options[0].name)
            elif option.type is OptionType.SUB_COMMAND:
                options = option.options or []
                sub_command = command.get_command(option.name)
            else:
                raise Exception()
            task = self._handle_callback(
                sub_command.callback,
                context,
                command.obj,
                **{option.name: resolve_argument(event.interaction, option) for option in options},
            )
        self.loop.create_task(task, name=f"interaction (id: {event.interaction.id})")

    async def sync_commands(self) -> None:
        _LOGGER.debug("syncing global commands...")
        application = await self.bot.rest.fetch_application()
        commands = await self.bot.rest.set_application_commands(
            application, tuple(self.builder.build_commands(self._commands.values()))  # type: ignore
        )
        for remote in commands:
            try:
                self.commands[remote.id] = self._commands.pop(remote.name)
            except KeyError:
                _LOGGER.error("failed to map command '%s' (ID: %s)", remote.name, remote.id)
        _LOGGER.info("synced commands")
        if self._commands:
            _LOGGER.warning("not all commands was synced")
            self._commands.clear()
        else:
            _LOGGER.debug("all commands was synced")

    async def _handle_callback(
        self,
        callback: CommandCallbackT,
        context: CommandInteractionContext,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        try:
            await callback(*args, context, **kwargs)
        except Exception as error:
            if self.bot.event_manager.get_listeners(CommandCallbackErrorEvent):
                _LOGGER.debug("exception occurred in command %s callback: %s", context.interaction.command_name, error)
                event: CommandCallbackErrorEvent = CommandCallbackErrorEvent(
                    exception=error, context=context
                )
                self.bot.event_manager.dispatch(event)
            else:
                _LOGGER.error(
                    "exception occurred in command %s callback: %s",
                    context.interaction.command_name,
                    error,
                    exc_info=error,
                )
