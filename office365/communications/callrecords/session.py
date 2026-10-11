from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.communications.callrecords.endpoint import Endpoint
from office365.communications.callrecords.modality import Modality
from office365.communications.callrecords.segment import Segment
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.communications.callrecords.failure_info import FailureInfo


class Session(Entity):
    """Represents a user-user communication or a user-meeting communication in the case of a conference call."""

    @property
    def segments(self) -> EntityCollection[Segment]:
        """
        The list of segments involved in the session.
        """
        return self.properties.get(
            "segments", EntityCollection(self.context, Segment, ResourcePath("segments", self.resource_path))
        )

    @property
    def callee(self) -> Endpoint:
        """Gets the callee property"""
        return self.properties.get("callee", Endpoint())

    @property
    def caller(self) -> Endpoint:
        """Gets the caller property"""
        return self.properties.get("caller", Endpoint())

    @odata(name="endDateTime")
    @property
    def end_date_time(self) -> datetime:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def is_test(self) -> Optional[bool]:
        """Gets the isTest property"""
        return self.properties.get("isTest", None)

    @property
    def modalities(self) -> ClientValueCollection[Modality]:
        """Gets the modalities property"""
        return self.properties.get("modalities", ClientValueCollection[Modality](Modality))

    @odata(name="startDateTime")
    @property
    def start_date_time(self) -> datetime:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.Session"

    @property
    def failure_info(self) -> FailureInfo:
        """Gets the failureInfo property"""
        from office365.communications.callrecords.failure_info import FailureInfo

        return self.properties.get("failureInfo", FailureInfo())
