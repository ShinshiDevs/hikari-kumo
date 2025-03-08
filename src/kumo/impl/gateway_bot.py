from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from hikari.events import InteractionCreateEvent
from hikari.impl import gateway_bot
from hikari.interactions import InteractionType
from hikari.internal import data_binding

from kumo.impl.command_handler import CommandHandler

if TYPE_CHECKING:
    from concurrent.futures import Executor
    from os import PathLike

    from hikari.guilds import PartialGuild
    from hikari.impl import CacheSettings, HTTPSettings, ProxySettings
    from hikari.intents import Intents
    from hikari.snowflakes import SnowflakeishOr

    from kumo.commands.types import CommandT
    from kumo.i18n.abc.ilocalization_provider import ILocalizationProvider

__all__: Sequence[str] = ()


class GatewayBot(gateway_bot.GatewayBot):
    def __init__(
        self,
        token: str,
        *,
        i18n: ILocalizationProvider | None = None,
        allow_color: bool = True,
        banner: str | None = "hikari",
        suppress_optimization_warning: bool = False,
        executor: Executor | None = None,
        force_color: bool = False,
        cache_settings: CacheSettings | None = None,
        http_settings: HTTPSettings | None = None,
        dumps: Callable[[Sequence[Any] | Mapping[str, Any]], bytes] = data_binding.default_json_dumps,
        loads: Callable[
            [str | bytes], data_binding.JSONArray | data_binding.JSONObject
        ] = data_binding.default_json_loads,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        auto_chunk_members: bool = True,
        logs: None | str | int | dict[str, Any] | PathLike[str] = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: ProxySettings | None = None,
        rest_url: str | None = None,
        sync_commands_flag: bool = True,
        default_guild: SnowflakeishOr[PartialGuild] | None = None,
    ) -> None:
        super().__init__(
            token,
            allow_color=allow_color,
            banner=banner,
            suppress_optimization_warning=suppress_optimization_warning,
            executor=executor,
            force_color=force_color,
            cache_settings=cache_settings,
            http_settings=http_settings,
            dumps=dumps,
            loads=loads,
            intents=intents,
            auto_chunk_members=auto_chunk_members,
            logs=logs,
            max_rate_limit=max_rate_limit,
            max_retries=max_retries,
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )
        self.commands: CommandHandler = CommandHandler(self, i18n=i18n)
        self.event_manager.subscribe(InteractionCreateEvent, self.on_interaction)

    async def on_interaction(self, event: InteractionCreateEvent) -> None:
        if event.interaction.type is InteractionType.APPLICATION_COMMAND:
            await self.commands.dispatch(event)

    def init_command(self, command: CommandT) -> CommandT:
        command.obj = command.obj()
        return command

    def add_command(self, command: CommandT) -> None:
        command = self.init_command(command)
        self.commands.add_command(command)
