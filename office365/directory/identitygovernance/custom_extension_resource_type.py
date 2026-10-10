from __future__ import annotations

from enum import Enum


class CustomExtensionResourceType(Enum):
    entraRoles = "1"
    azureResources = "2"
    entraGroups = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomExtensionResourceType"
