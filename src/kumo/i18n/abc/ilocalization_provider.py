from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

from hikari.locales import Locale

from kumo.i18n.types import Localized

__all__: Sequence[str] = ("ILocalizationProvider",)


class ILocalizationProvider(Protocol):
    __slots__: Sequence[str] = ()

    def localize(self, value: Localized) -> tuple[Mapping[Locale | str, str], str]: ...
