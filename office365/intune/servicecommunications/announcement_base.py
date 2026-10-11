from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.runtime.types.key_value_pair import KeyValuePair


class ServiceAnnouncementBase(Entity):
    """This is an abstract base type for serviceHealthIssue and serviceUpdateMessage."""

    @property
    def details(self) -> ClientValueCollection[KeyValuePair]:
        """Gets the details property"""
        from office365.runtime.types.key_value_pair import KeyValuePair

        return self.properties.get("details", ClientValueCollection[KeyValuePair](KeyValuePair))

    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceAnnouncementBase"
