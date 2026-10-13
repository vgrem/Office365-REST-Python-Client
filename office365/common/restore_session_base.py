from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.backuprestore.restorejobtype import RestoreJobType
    from office365.backuprestore.restoresessions.artifact_count import (
        RestoreSessionArtifactCount,
    )
    from office365.backuprestore.restoresessions.status import RestoreSessionStatus
    from office365.directory.identity_set import IdentitySet
    from office365.runtime.types.public_error import PublicError


class RestoreSessionBase(Entity):
    def activate(self) -> Self:
        """Activate the restore session so the restore job starts.

        A freshly created restore session is in the ``draft`` state; activating it
        moves it through ``activating`` to ``active`` / ``completed``.
        """
        qry = ServiceOperationQuery(self, "activate", return_type=self)
        self.context.add_query(qry)
        return self

    @property
    def completed_date_time(self) -> Optional[datetime]:
        """Gets the completedDateTime property"""
        return self.properties.get("completedDateTime", datetime.min)

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
    def restore_job_type(self) -> RestoreJobType:
        """Gets the restoreJobType property"""
        from office365.backuprestore.restorejobtype import RestoreJobType

        return self.properties.get("restoreJobType", RestoreJobType.standard)

    @property
    def restore_session_artifact_count(self) -> RestoreSessionArtifactCount:
        """Gets the restoreSessionArtifactCount property"""
        from office365.backuprestore.restoresessions.artifact_count import (
            RestoreSessionArtifactCount,
        )

        return self.properties.get("restoreSessionArtifactCount", RestoreSessionArtifactCount())

    @property
    def status(self) -> RestoreSessionStatus:
        """Gets the status property"""
        from office365.backuprestore.restoresessions.status import RestoreSessionStatus

        return self.properties.get("status", RestoreSessionStatus.draft)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RestoreSessionBase"
