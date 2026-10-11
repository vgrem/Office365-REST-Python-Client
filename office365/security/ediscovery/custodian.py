from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.ediscovery.ediscovery_index_operation import (
        EdiscoveryIndexOperation,
    )
    from office365.security.site_source import SiteSource
    from office365.security.unified_group_source import UnifiedGroupSource
    from office365.security.user_source import UserSource


class EdiscoveryCustodian(Entity):
    @property
    def acknowledged_date_time(self) -> Optional[datetime]:
        """Gets the acknowledgedDateTime property"""
        return self.properties.get("acknowledgedDateTime", datetime.min)

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryCustodian"

    @property
    def last_index_operation(self) -> EdiscoveryIndexOperation:
        """Gets the lastIndexOperation property"""
        from office365.security.ediscovery.ediscovery_index_operation import (
            EdiscoveryIndexOperation,
        )

        return self.properties.get(
            "lastIndexOperation",
            EdiscoveryIndexOperation(self.context, ResourcePath("lastIndexOperation", self.resource_path)),
        )

    @property
    def site_sources(self) -> EntityCollection[SiteSource]:
        """Gets the siteSources property"""
        from office365.security.site_source import SiteSource

        return self.properties.get(
            "siteSources",
            EntityCollection[SiteSource](self.context, SiteSource, ResourcePath("siteSources", self.resource_path)),
        )

    @property
    def unified_group_sources(self) -> EntityCollection[UnifiedGroupSource]:
        """Gets the unifiedGroupSources property"""
        from office365.security.unified_group_source import UnifiedGroupSource

        return self.properties.get(
            "unifiedGroupSources",
            EntityCollection[UnifiedGroupSource](
                self.context, UnifiedGroupSource, ResourcePath("unifiedGroupSources", self.resource_path)
            ),
        )

    @property
    def user_sources(self) -> EntityCollection[UserSource]:
        """Gets the userSources property"""
        from office365.security.user_source import UserSource

        return self.properties.get(
            "userSources",
            EntityCollection[UserSource](self.context, UserSource, ResourcePath("userSources", self.resource_path)),
        )
