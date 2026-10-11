from __future__ import annotations

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.collaboration.analyzed_email import AnalyzedEmail


class CollaborationRoot(Entity):
    @property
    def analyzed_emails(self) -> EntityCollection[AnalyzedEmail]:
        """Gets the analyzedEmails property"""
        return self.properties.get(
            "analyzedEmails",
            EntityCollection[AnalyzedEmail](
                self.context, AnalyzedEmail, ResourcePath("analyzedEmails", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CollaborationRoot"
