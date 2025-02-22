from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import attrs
from hikari.channels import ChannelType
from hikari.undefined import UNDEFINED, UndefinedOr

from kumo.i18n.types import LocalizedOr

__all__: Sequence[str] = ("Choice", "Option")


@attrs.define(kw_only=True, slots=True, frozen=True)
class Choice:
    name: str = attrs.field(repr=True, eq=False)
    value: Any = attrs.field(repr=True, eq=True)

    display_name: LocalizedOr[str] = attrs.field(repr=False, eq=False)


@attrs.define(kw_only=True, slots=True, frozen=True)
class Option:
    name: str = attrs.field(repr=True, eq=True)

    display_name: LocalizedOr[str] = attrs.field(repr=False, eq=False)
    description: LocalizedOr[str] = attrs.field(repr=False, eq=False)

    choices: Sequence[Choice] = attrs.field(factory=tuple, repr=True, eq=False)

    min_value: UndefinedOr[int] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    max_value: UndefinedOr[int] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    min_length: UndefinedOr[int] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    max_length: UndefinedOr[int] = attrs.field(default=UNDEFINED, repr=False, eq=False)
    channel_types: Sequence[ChannelType] = attrs.field(factory=tuple, repr=False, eq=False)
