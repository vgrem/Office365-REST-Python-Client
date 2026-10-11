from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class GitHubRepoEvidence(ClientValue):
    baseUrl: str | None = None
    login: str | None = None
    owner: str | None = None
    ownerType: str | None = None
    repoId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.GitHubRepoEvidence"
