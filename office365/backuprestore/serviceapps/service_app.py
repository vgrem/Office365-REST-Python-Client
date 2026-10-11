from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.backuprestore.serviceapps.status import ServiceAppStatus
    from office365.directory.identity_set import IdentitySet
    from office365.directory.permissions.identity import Identity


class ServiceApp(Entity):
    @property
    def application(self) -> Identity:
        """Gets the application property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("application", Identity())

    @property
    def effective_date_time(self) -> Optional[datetime]:
        """Gets the effectiveDateTime property"""
        return self.properties.get("effectiveDateTime", datetime.min)

    @property
    def last_modified_by(self) -> IdentitySet:
        """Gets the lastModifiedBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("lastModifiedBy", IdentitySet())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def registration_date_time(self) -> Optional[datetime]:
        """Gets the registrationDateTime property"""
        return self.properties.get("registrationDateTime", datetime.min)

    @property
    def status(self) -> ServiceAppStatus:
        """Gets the status property"""
        from office365.backuprestore.serviceapps.status import ServiceAppStatus

        return self.properties.get("status", ServiceAppStatus.inactive)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceApp"
