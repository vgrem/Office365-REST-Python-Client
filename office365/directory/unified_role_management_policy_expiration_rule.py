from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.runtime.types.duration import timedelta


class UnifiedRoleManagementPolicyExpirationRule(Entity):
    @property
    def is_expiration_required(self) -> Optional[bool]:
        """Gets the isExpirationRequired property"""
        return self.properties.get("isExpirationRequired", None)

    @property
    def maximum_duration(self) -> Optional[timedelta]:
        """Gets the maximumDuration property"""
        return self.properties.get("maximumDuration", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyExpirationRule"
