from __future__ import annotations

from collections.abc import Sequence

import attrs

__all__: Sequence[str] = ("Metadata",)


@attrs.define(kw_only=True, weakref_slot=False)
class Metadata:
    name: str = attrs.field(repr=True, eq=True)
