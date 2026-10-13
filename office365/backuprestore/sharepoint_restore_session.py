from __future__ import annotations

from typing import TYPE_CHECKING

from office365.common.restore_session_base import RestoreSessionBase
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.granular_site_restore_artifact import (
        GranularSiteRestoreArtifact,
    )
    from office365.common.site_restore_artifact import SiteRestoreArtifact
    from office365.common.site_restore_artifacts_bulk_addition_request import (
        SiteRestoreArtifactsBulkAdditionRequest,
    )


class SharePointRestoreSession(RestoreSessionBase):
    @property
    def granular_site_restore_artifacts(self) -> EntityCollection[GranularSiteRestoreArtifact]:
        """Gets the granularSiteRestoreArtifacts property"""
        from office365.common.granular_site_restore_artifact import (
            GranularSiteRestoreArtifact,
        )

        return self.properties.get(
            "granularSiteRestoreArtifacts",
            EntityCollection[GranularSiteRestoreArtifact](
                self.context,
                GranularSiteRestoreArtifact,
                ResourcePath("granularSiteRestoreArtifacts", self.resource_path),
            ),
        )

    @property
    def site_restore_artifacts(self) -> EntityCollection[SiteRestoreArtifact]:
        """Gets the siteRestoreArtifacts property"""
        from office365.common.site_restore_artifact import SiteRestoreArtifact

        return self.properties.get(
            "siteRestoreArtifacts",
            EntityCollection[SiteRestoreArtifact](
                self.context, SiteRestoreArtifact, ResourcePath("siteRestoreArtifacts", self.resource_path)
            ),
        )

    @property
    def site_restore_artifacts_bulk_addition_requests(self) -> EntityCollection[SiteRestoreArtifactsBulkAdditionRequest]:
        """Gets the siteRestoreArtifactsBulkAdditionRequests property"""
        from office365.common.site_restore_artifacts_bulk_addition_request import (
            SiteRestoreArtifactsBulkAdditionRequest,
        )

        return self.properties.get(
            "siteRestoreArtifactsBulkAdditionRequests",
            EntityCollection[SiteRestoreArtifactsBulkAdditionRequest](
                self.context,
                SiteRestoreArtifactsBulkAdditionRequest,
                ResourcePath("siteRestoreArtifactsBulkAdditionRequests", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SharePointRestoreSession"
