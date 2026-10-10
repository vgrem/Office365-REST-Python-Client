from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.platformtype import DevicePlatformType


@dataclass
class AnswerVariant(ClientValue):
    description: str | None = None
    displayName: str | None = None
    languageTag: str | None = None
    platform: DevicePlatformType = DevicePlatformType.android
    webUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.search.AnswerVariant"
