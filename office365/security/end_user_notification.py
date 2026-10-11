from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.permissions.email_identity import EmailIdentity
    from office365.security.attacksimulations.endusernotificationtype import (
        EndUserNotificationType,
    )
    from office365.security.attacksimulations.simulationcontentsource import (
        SimulationContentSource,
    )
    from office365.security.attacksimulations.simulationcontentstatus import (
        SimulationContentStatus,
    )
    from office365.security.end_user_notification_detail import (
        EndUserNotificationDetail,
    )


class EndUserNotification(Entity):
    @property
    def created_by(self) -> EmailIdentity:
        """Gets the createdBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("createdBy", EmailIdentity())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_by(self) -> EmailIdentity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("lastModifiedBy", EmailIdentity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def notification_type(self) -> EndUserNotificationType:
        """Gets the notificationType property"""
        from office365.security.attacksimulations.endusernotificationtype import (
            EndUserNotificationType,
        )

        return self.properties.get("notificationType", EndUserNotificationType.unknown)

    @property
    def source(self) -> SimulationContentSource:
        """Gets the source property"""
        from office365.security.attacksimulations.simulationcontentsource import (
            SimulationContentSource,
        )

        return self.properties.get("source", SimulationContentSource.unknown)

    @property
    def status(self) -> SimulationContentStatus:
        """Gets the status property"""
        from office365.security.attacksimulations.simulationcontentstatus import (
            SimulationContentStatus,
        )

        return self.properties.get("status", SimulationContentStatus.unknown)

    @property
    def supported_locales(self) -> StringCollection:
        """Gets the supportedLocales property"""
        return self.properties.get("supportedLocales", StringCollection())

    @property
    def details(self) -> EntityCollection[EndUserNotificationDetail]:
        """Gets the details property"""
        from office365.security.end_user_notification_detail import (
            EndUserNotificationDetail,
        )

        return self.properties.get(
            "details",
            EntityCollection[EndUserNotificationDetail](
                self.context, EndUserNotificationDetail, ResourcePath("details", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EndUserNotification"
