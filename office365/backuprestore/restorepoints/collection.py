from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

from office365.common.restore_point import RestorePoint
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.backuprestore.artifact_query import ArtifactQuery
    from office365.backuprestore.restorepoints.preference import RestorePointPreference
    from office365.backuprestore.restorepoints.search_response import (
        RestorePointSearchResponse,
    )
    from office365.backuprestore.restorepoints.tags import RestorePointTags
    from office365.backuprestore.time_period import TimePeriod


class RestorePointCollection(EntityCollection[RestorePoint]):
    """The tenant's protected restore points.

    Restore points are addressed through the
    ``POST /solutions/backupRestore/restorePoints/search`` action rather than by
    plain enumeration; use :meth:`search` to locate the point to restore from.
    """

    def search(
        self,
        protection_unit_ids: Optional[Sequence[str]] = None,
        protection_time_period: Optional[TimePeriod] = None,
        restore_point_preference: Optional[RestorePointPreference] = None,
        tags: Optional[RestorePointTags] = None,
        artifact_query: Optional[ArtifactQuery] = None,
    ) -> ClientResult[RestorePointSearchResponse]:
        """Search the restore points of the specified protection units.

        Args:
            protection_unit_ids: Restrict the search to these protection unit ids
                (mailbox, drive or site protection units).
            protection_time_period: Restrict the search to points created in this window.
            restore_point_preference: When several points match, prefer the ``latest``
                or the ``oldest`` one.
            tags: Restrict the search to points carrying these tags.
            artifact_query: Further restrict the artifacts (for example message search).
        """
        from office365.backuprestore.restorepoints.search_response import (
            RestorePointSearchResponse,
        )

        return_type = ClientResult(self.context, RestorePointSearchResponse())
        payload = {
            "protectionUnitIds": list(protection_unit_ids) if protection_unit_ids is not None else None,
            "protectionTimePeriod": protection_time_period,
            "restorePointPreference": restore_point_preference.name if restore_point_preference is not None else None,
            "tags": tags.name if tags is not None else None,
            "artifactQuery": artifact_query,
        }
        qry = ServiceOperationQuery(self, "search", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
