from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.platformtype import DevicePlatformType
from office365.runtime.client_value import ClientValue


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
