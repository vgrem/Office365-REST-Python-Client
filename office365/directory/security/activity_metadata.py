from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.useractivitytype import UserActivityType
from office365.runtime.client_value import ClientValue


@dataclass
class ActivityMetadata(ClientValue):
    activity: UserActivityType = UserActivityType.uploadText

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ActivityMetadata"
