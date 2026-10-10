from __future__ import annotations

from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.webs.time_zone_information import TimeZoneInformation


class TimeZone(Entity):
    """Represents the time zone setting that is implemented on a SharePoint Web site."""

    def local_time_to_utc(self, date: datetime) -> ClientResult[datetime]:
        """Converts the specified date from local time to Coordinated Universal Time (UTC).

        Args:
            date (datetime): The local date and time value to convert.
        """
        result = ClientResult[datetime](self.context, datetime.min)
        params = {"date": date.isoformat()}
        qry = ServiceOperationQuery(self, "LocalTimeToUTC", None, params, None, result)
        self.context.add_query(qry)
        return result

    def set_id(self, id_) -> Self:
        """Args:
        id_ (int):
        """
        qry = ServiceOperationQuery(self, "SetId", [id_], None, None, None)
        self.context.add_query(qry)
        return self

    @property
    def id(self) -> Optional[int]:
        """Gets the identifier of the time zone."""
        return self.properties.get("Id", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description of the time zone."""
        return self.properties.get("Description", None)

    @property
    def information(self) -> TimeZoneInformation:
        """Gets information about the time zone."""
        return self.properties.get("Information", TimeZoneInformation())

    def utc_to_local_time(self, date: datetime) -> ClientResult[datetime]:
        """UTCToLocalTime operation.

        Args:
            date (datetime):
                date parameter
        """
        return_type = ClientResult(self.context, datetime.min)
        qry = FunctionQuery(self, "UTCToLocalTime", [date], return_type)
        self.context.add_query(qry)
        return return_type


class TimeZoneCollection(EntityCollection[TimeZone]):
    """TimeZone collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, TimeZone, resource_path)
