from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from kumo.i18n.localized import Localized

__all__: Sequence[str] = ("LocalizedOr",)

T = TypeVar("T")
LocalizedOr = Localized | T
