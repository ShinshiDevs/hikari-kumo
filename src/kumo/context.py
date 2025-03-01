from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

import attrs
from hikari.api import ComponentBuilder
from hikari.channels import TextableGuildChannel
from hikari.embeds import Embed
from hikari.files import Resourceish
from hikari.guilds import GatewayGuild, PartialRole
from hikari.interactions import CommandInteraction, InteractionMember, PartialInteraction, ResponseType
from hikari.messages import Message, MessageFlag
from hikari.snowflakes import SnowflakeishSequence
from hikari.undefined import UNDEFINED, UndefinedOr
from hikari.users import PartialUser, User

from kumo.traits import BotAware

__all__: Sequence[str] = ("CommandInteractionContext",)

T = TypeVar("T", bound=PartialInteraction)


@attrs.define(kw_only=True, weakref_slot=False)
class InteractionContext(Generic[T]):
    bot: BotAware
    interaction: T

    async def defer(self, flags: MessageFlag = MessageFlag.NONE, *, ephemeral: bool = False) -> None:
        if ephemeral:
            flags |= MessageFlag.EPHEMERAL
        return await self.bot.rest.create_interaction_response(
            interaction=self.interaction.id,
            token=self.interaction.token,
            flags=flags,
            response_type=ResponseType.DEFERRED_MESSAGE_CREATE,
        )

    async def create_response(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        flags: MessageFlag = MessageFlag.NONE,
        ephemeral: bool = False,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
    ) -> None:
        if ephemeral:
            flags |= MessageFlag.EPHEMERAL
        return await self.bot.rest.create_interaction_response(
            interaction=self.interaction.id,
            response_type=ResponseType.MESSAGE_CREATE,
            token=self.interaction.token,
            content=content,
            flags=flags,
            attachment=attachment,
            attachments=attachments,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            mentions_everyone=mentions_everyone,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

    async def edit_response(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
    ) -> Message | None:
        return await self.bot.rest.edit_interaction_response(
            application=self.interaction.application_id,
            token=self.interaction.token,
            content=content,
            attachment=attachment,
            attachments=attachments,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
        )

    async def delete_response(self) -> None:
        await self.bot.rest.delete_interaction_response(
            application=self.interaction.application_id, token=self.interaction.token
        )


@attrs.define(kw_only=True, weakref_slot=False)
class CommandInteractionContext(InteractionContext[CommandInteraction]):
    @property
    def user(self) -> User:
        return self.interaction.user

    @property
    def member(self) -> InteractionMember | None:
        return self.interaction.member

    @property
    def guild(self) -> GatewayGuild | None:
        return self.interaction.get_guild()

    @property
    def channel(self) -> TextableGuildChannel | None:
        return self.interaction.get_channel()
