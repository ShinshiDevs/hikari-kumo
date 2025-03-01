from __future__ import annotations

from collections.abc import Sequence

import attrs
from hikari.permissions import Permissions
from hikari.undefined import UNDEFINED, UndefinedOr

from kumo.commands.options import Option
from kumo.i18n.types import LocalizedOr
from kumo.metadata import Metadata

__all__: Sequence[str] = (
    "CommandMetadata",
    "ApplicationMetadata",
    "SubCommandMetadata",
    "UserCommandMetadata",
    "MessageCommandMetadata",
    "SlashCommandMetadata",
)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class CommandMetadata(Metadata):
    display_name: LocalizedOr[str] = attrs.field(repr=False, eq=False)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class ApplicationMetadata(CommandMetadata):
    default_member_permissions: UndefinedOr[Permissions] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    is_dm_enabled: UndefinedOr[bool] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    is_nsfw: UndefinedOr[bool] = attrs.field(default=UNDEFINED, repr=False, eq=False)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class SubCommandMetadata(CommandMetadata):
    description: LocalizedOr[str] = attrs.field(repr=False, eq=False)

    options: Sequence[Option] = attrs.field(factory=tuple, repr=False, eq=False)


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class UserCommandMetadata(ApplicationMetadata): ...


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class MessageCommandMetadata(ApplicationMetadata): ...


@attrs.define(kw_only=True, weakref_slot=False, slots=False)
class SlashCommandMetadata(ApplicationMetadata, SubCommandMetadata): ...
