from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.onlinemeetings.attendance_record import (
        AttendanceRecord,
    )
    from office365.communications.virtualevents.external_information import (
        VirtualEventExternalInformation,
    )


class MeetingAttendanceReport(Entity):
    @property
    def external_event_information(self) -> ClientValueCollection[VirtualEventExternalInformation]:
        """Gets the externalEventInformation property"""
        from office365.communications.virtualevents.external_information import (
            VirtualEventExternalInformation,
        )

        return self.properties.get(
            "externalEventInformation",
            ClientValueCollection[VirtualEventExternalInformation](VirtualEventExternalInformation),
        )

    @property
    def meeting_end_date_time(self) -> Optional[datetime]:
        """Gets the meetingEndDateTime property"""
        return self.properties.get("meetingEndDateTime", datetime.min)

    @property
    def meeting_start_date_time(self) -> Optional[datetime]:
        """Gets the meetingStartDateTime property"""
        return self.properties.get("meetingStartDateTime", datetime.min)

    @property
    def total_participant_count(self) -> Optional[int]:
        """Gets the totalParticipantCount property"""
        return self.properties.get("totalParticipantCount", None)

    @property
    def attendance_records(self) -> EntityCollection[AttendanceRecord]:
        """Gets the attendanceRecords property"""
        from office365.communications.onlinemeetings.attendance_record import (
            AttendanceRecord,
        )

        return self.properties.get(
            "attendanceRecords",
            EntityCollection[AttendanceRecord](
                self.context, AttendanceRecord, ResourcePath("attendanceRecords", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MeetingAttendanceReport"
