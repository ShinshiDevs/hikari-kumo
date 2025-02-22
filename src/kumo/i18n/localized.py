from __future__ import annotations

from collections.abc import Sequence

import attrs

__all__: Sequence[str] = ("Localized",)


@attrs.define(slots=True, frozen=True)
class Localized:
    key: str = attrs.field(repr=True, eq=True)
    fallback: str = attrs.field(kw_only=True, repr=True, eq=False)
