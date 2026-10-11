from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.onedrive.sensitivitylabels.usagerights import UsageRights


class UsageRightsIncluded(Entity):
    @property
    def owner_email(self) -> Optional[str]:
        """Gets the ownerEmail property"""
        return self.properties.get("ownerEmail", None)

    @property
    def user_email(self) -> Optional[str]:
        """Gets the userEmail property"""
        return self.properties.get("userEmail", None)

    @property
    def value(self) -> UsageRights:
        """Gets the value property"""
        from office365.onedrive.sensitivitylabels.usagerights import UsageRights

        return self.properties.get("value", UsageRights.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UsageRightsIncluded"
