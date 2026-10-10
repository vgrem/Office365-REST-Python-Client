from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class MoveJobEntityData(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.MoveJobEntityData"

    @property
    def api_version(self) -> Optional[str]:
        """Gets the ApiVersion property"""
        return self.properties.get("ApiVersion", None)

    @property
    def batch_id(self) -> Optional[UUID]:
        """Gets the BatchId property"""
        return self.properties.get("BatchId", None)

    @property
    def cancel_triggered_by(self) -> Optional[str]:
        """Gets the CancelTriggeredBy property"""
        return self.properties.get("CancelTriggeredBy", None)

    @property
    def destination_data_location(self) -> Optional[str]:
        """Gets the DestinationDataLocation property"""
        return self.properties.get("DestinationDataLocation", None)

    @property
    def direction(self) -> Optional[int]:
        """Gets the Direction property"""
        return self.properties.get("Direction", None)

    @property
    def error_message(self) -> Optional[str]:
        """Gets the ErrorMessage property"""
        return self.properties.get("ErrorMessage", None)

    @property
    def finished_date_in_utc(self) -> Optional[datetime]:
        """Gets the FinishedDateInUtc property"""
        return self.properties.get("FinishedDateInUtc", datetime.min)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def is_read_only_alert_raised(self) -> Optional[bool]:
        """Gets the IsReadOnlyAlertRaised property"""
        return self.properties.get("IsReadOnlyAlertRaised", None)

    @property
    def job_phase(self) -> Optional[int]:
        """Gets the JobPhase property"""
        return self.properties.get("JobPhase", None)

    @property
    def notify(self) -> Optional[str]:
        """Gets the Notify property"""
        return self.properties.get("Notify", None)

    @property
    def option(self) -> Optional[int]:
        """Gets the Option property"""
        return self.properties.get("Option", None)

    @property
    def preferred_move_begin_date_in_utc(self) -> Optional[datetime]:
        """Gets the PreferredMoveBeginDateInUtc property"""
        return self.properties.get("PreferredMoveBeginDateInUtc", datetime.min)

    @property
    def preferred_move_end_date_in_utc(self) -> Optional[datetime]:
        """Gets the PreferredMoveEndDateInUtc property"""
        return self.properties.get("PreferredMoveEndDateInUtc", datetime.min)

    @property
    def reserve(self) -> Optional[str]:
        """Gets the Reserve property"""
        return self.properties.get("Reserve", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def source_data_location(self) -> Optional[str]:
        """Gets the SourceDataLocation property"""
        return self.properties.get("SourceDataLocation", None)

    @property
    def state(self) -> Optional[int]:
        """Gets the State property"""
        return self.properties.get("State", None)

    @property
    def sub_type(self) -> Optional[int]:
        """Gets the SubType property"""
        return self.properties.get("SubType", None)

    @property
    def triggered_by(self) -> Optional[str]:
        """Gets the TriggeredBy property"""
        return self.properties.get("TriggeredBy", None)

    @property
    def type(self) -> Optional[int]:
        """Gets the Type property"""
        return self.properties.get("Type", None)
