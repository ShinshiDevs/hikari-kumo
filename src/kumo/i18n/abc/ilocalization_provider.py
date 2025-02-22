from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

__all__: Sequence[str] = ("ILocalizationProvider",)


class ILocalizationProvider(Protocol):
    __slots__: Sequence[str] = ()
