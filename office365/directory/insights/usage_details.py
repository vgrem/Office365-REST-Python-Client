from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class UsageDetails(ClientValue):
    """Complex type containing properties of Used items. Information on when the resource was last accessed (viewed)
    or modified (edited) by the user.

    Args:
        last_accessed_datetime: The date and time the resource was last accessed by the user.
        last_modified_datetime: The date and time the resource was last modified by the user.
    """

    lastAccessedDateTime: datetime | None = None
    lastModifiedDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UsageDetails"
