from __future__ import annotations

from collections.abc import Sequence

import attrs

__all__: Sequence[str] = ("Metadata",)


@attrs.define(kw_only=True, slots=True, frozen=True)
class Metadata:
    name: str = attrs.field(repr=True, eq=True)
