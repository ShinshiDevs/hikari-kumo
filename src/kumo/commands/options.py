from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import attrs
from hikari.channels import ChannelType
from hikari.commands import OptionType

from kumo.i18n.types import LocalizedOr

__all__: Sequence[str] = ("Choice", "Option")


@attrs.define(kw_only=True, weakref_slot=False, frozen=True)
class Choice:
    name: str = attrs.field(repr=True, eq=False)
    value: Any = attrs.field(repr=True, eq=True)

    display_name: LocalizedOr[str] = attrs.field(repr=False, eq=False)


@attrs.define(kw_only=True, weakref_slot=False, frozen=True)
class Option:
    type: OptionType = attrs.field(repr=True, eq=True)
    name: str = attrs.field(repr=True, eq=True)

    display_name: LocalizedOr[str] = attrs.field(repr=False, eq=False)
    description: LocalizedOr[str] = attrs.field(repr=False, eq=False)

    choices: Sequence[Choice] = attrs.field(factory=tuple, repr=True, eq=True)

    is_required: bool = attrs.field(default=True, repr=True, eq=True)
    min_value: int | float | None = attrs.field(default=None, repr=False, eq=False)
    max_value: int | float | None = attrs.field(default=None, repr=False, eq=False)
    min_length: int | None = attrs.field(default=None, repr=False, eq=False)
    max_length: int | None = attrs.field(default=None, repr=False, eq=False)
    channel_types: Sequence[ChannelType] = attrs.field(factory=tuple, repr=False, eq=False)
