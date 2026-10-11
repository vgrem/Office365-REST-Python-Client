from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from office365.booking.phone import Phone
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection


@dataclass
class OnlineMeetingInfo(ClientValue):
    conferenceId: str | None = None
    joinUrl: str | None = None
    phones: ClientValueCollection[Phone] = field(default_factory=lambda: ClientValueCollection(Phone))
    quickDial: str | None = None
    tollFreeNumbers: StringCollection = field(default_factory=StringCollection)
    tollNumber: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnlineMeetingInfo"

    @property
    def join_url(self) -> Optional[str]:
        """The join link (snake_case alias for the ``joinUrl`` field)."""
        return self.joinUrl
