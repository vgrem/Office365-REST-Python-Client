from __future__ import annotations

from dataclasses import dataclass

from office365.directory.permissions.identity import Identity
from office365.runtime.client_value import ClientValue


@dataclass
class SubjectRightsRequestIdentity(ClientValue):
    """Represents the identity of the data subject for a subject rights request."""

    displayName: str | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    objectIdentity: Identity | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.subjectRightsRequestSubjectIdentity"
