from __future__ import annotations

from collections.abc import Sequence

__all__: Sequence[str] = ("NameTuple",)

NameTuple = tuple[str] | tuple[str, str]
