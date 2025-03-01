from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from hikari.applications import Application
from hikari.traits import EventManagerAware, RESTAware

from kumo.i18n.abc.ilocalization_provider import ILocalizationProvider

__all__: Sequence[str] = ("BotAware",)


@runtime_checkable
class BotAware(RESTAware, EventManagerAware, Protocol):
    __slots__: Sequence[str] = ()

    @property
    @abstractmethod
    def application(self) -> Application:
        raise NotImplementedError

    @property
    @abstractmethod
    def i18n(self) -> ILocalizationProvider:
        raise NotImplementedError
