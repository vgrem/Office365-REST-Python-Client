from __future__ import annotations

from typing import TYPE_CHECKING

from office365.common.restore_session_base import RestoreSessionBase
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.granular_mailbox_restore_artifact import (
        GranularMailboxRestoreArtifact,
    )
    from office365.common.mailbox_restore_artifact import MailboxRestoreArtifact
    from office365.common.mailbox_restore_artifacts_bulk_addition_request import (
        MailboxRestoreArtifactsBulkAdditionRequest,
    )


class ExchangeRestoreSession(RestoreSessionBase):
    @property
    def granular_mailbox_restore_artifacts(self) -> EntityCollection[GranularMailboxRestoreArtifact]:
        """Gets the granularMailboxRestoreArtifacts property"""
        from office365.common.granular_mailbox_restore_artifact import (
            GranularMailboxRestoreArtifact,
        )

        return self.properties.get(
            "granularMailboxRestoreArtifacts",
            EntityCollection[GranularMailboxRestoreArtifact](
                self.context,
                GranularMailboxRestoreArtifact,
                ResourcePath("granularMailboxRestoreArtifacts", self.resource_path),
            ),
        )

    @property
    def mailbox_restore_artifacts(self) -> EntityCollection[MailboxRestoreArtifact]:
        """Gets the mailboxRestoreArtifacts property"""
        from office365.common.mailbox_restore_artifact import MailboxRestoreArtifact

        return self.properties.get(
            "mailboxRestoreArtifacts",
            EntityCollection[MailboxRestoreArtifact](
                self.context, MailboxRestoreArtifact, ResourcePath("mailboxRestoreArtifacts", self.resource_path)
            ),
        )

    @property
    def mailbox_restore_artifacts_bulk_addition_requests(
        self,
    ) -> EntityCollection[MailboxRestoreArtifactsBulkAdditionRequest]:
        """Gets the mailboxRestoreArtifactsBulkAdditionRequests property"""
        from office365.common.mailbox_restore_artifacts_bulk_addition_request import (
            MailboxRestoreArtifactsBulkAdditionRequest,
        )

        return self.properties.get(
            "mailboxRestoreArtifactsBulkAdditionRequests",
            EntityCollection[MailboxRestoreArtifactsBulkAdditionRequest](
                self.context,
                MailboxRestoreArtifactsBulkAdditionRequest,
                ResourcePath("mailboxRestoreArtifactsBulkAdditionRequests", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExchangeRestoreSession"
