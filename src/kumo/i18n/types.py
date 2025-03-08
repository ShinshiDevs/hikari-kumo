from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import attrs

__all__: Sequence[str] = ("Localized", "LocalizedOr")


@attrs.define(slots=True, frozen=True)
class Localized:
    key: str = attrs.field(repr=True, eq=True)
    fallback: str = attrs.field(kw_only=True, repr=True, eq=False)


T = TypeVar("T")
LocalizedOr = Localized | T
