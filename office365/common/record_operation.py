from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation


class RecordOperation(PollableOperation, Entity):
    @property
    def recording_access_token(self) -> Optional[str]:
        """Gets the recordingAccessToken property"""
        return self.properties.get("recordingAccessToken", None)

    @property
    def recording_location(self) -> Optional[str]:
        """Gets the recordingLocation property"""
        return self.properties.get("recordingLocation", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RecordOperation"
