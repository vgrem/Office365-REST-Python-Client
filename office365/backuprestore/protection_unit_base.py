from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.directory.identity_set import IdentitySet
    from office365.directory.protection.source import ProtectionSource
    from office365.directory.protection.unitstatus import ProtectionUnitStatus
    from office365.runtime.types.public_error import PublicError


class ProtectionUnitBase(Entity):
    def offboard(self) -> Self:
        """Remove the protection unit from its protection policy.

        Offboarding is asynchronous: the unit stays in the policy until the operation
        completes and its ``offboard_requested_date_time`` is stamped.
        """
        qry = ServiceOperationQuery(self, "offboard", return_type=self)
        self.context.add_query(qry)
        return self

    def cancel_offboard(self) -> Self:
        """Cancel a pending offboard request for the protection unit."""
        qry = ServiceOperationQuery(self, "cancelOffboard", return_type=self)
        self.context.add_query(qry)
        return self

    @property
    def created_by(self) -> IdentitySet:
        """Gets the createdBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("createdBy", IdentitySet())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())

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
    def offboard_requested_date_time(self) -> Optional[datetime]:
        """Gets the offboardRequestedDateTime property"""
        return self.properties.get("offboardRequestedDateTime", datetime.min)

    @property
    def policy_id(self) -> Optional[str]:
        """Gets the policyId property"""
        return self.properties.get("policyId", None)

    @property
    def protection_sources(self) -> ProtectionSource:
        """Gets the protectionSources property"""
        from office365.directory.protection.source import ProtectionSource

        return self.properties.get("protectionSources", ProtectionSource.none)

    @property
    def status(self) -> ProtectionUnitStatus:
        """Gets the status property"""
        from office365.directory.protection.unitstatus import ProtectionUnitStatus

        return self.properties.get("status", ProtectionUnitStatus.protectRequested)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProtectionUnitBase"
