from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identity_set import IdentitySet
    from office365.directory.protection.rulestatus import ProtectionRuleStatus
    from office365.runtime.types.public_error import PublicError


class ProtectionRuleBase(Entity):
    """Represents a protection rule specified by the client as part of a protection plan applied to
    Microsoft 365 data in an organization. Currently, only inclusion rules, which are rules that indicate
    that a protection policy should match the specified criteria, can be defined.

    Currently, protection Rules are static in nature, meaning policy changes are applied only when the
    rule is executed, with no automatic/dynamic updates."""

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
    def is_auto_apply_enabled(self) -> Optional[bool]:
        """Gets the isAutoApplyEnabled property"""
        return self.properties.get("isAutoApplyEnabled", None)

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
    def status(self) -> ProtectionRuleStatus:
        """Gets the status property"""
        from office365.directory.protection.rulestatus import ProtectionRuleStatus

        return self.properties.get("status", ProtectionRuleStatus.draft)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProtectionRuleBase"
