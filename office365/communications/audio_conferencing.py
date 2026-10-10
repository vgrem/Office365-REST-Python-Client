from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class AudioConferencing(ClientValue):
    conferenceId: str | None = None
    dialinUrl: str | None = None
    tollFreeNumber: str | None = None
    tollFreeNumbers: StringCollection = field(default_factory=StringCollection)
    tollNumber: str | None = None
    tollNumbers: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AudioConferencing"
