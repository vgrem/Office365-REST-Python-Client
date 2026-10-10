from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.teams.teamwork.workforce_integration_encryption_protocol import (
    WorkforceIntegrationEncryptionProtocol,
)


@dataclass
class WorkforceIntegrationEncryption(ClientValue):
    protocol: WorkforceIntegrationEncryptionProtocol = WorkforceIntegrationEncryptionProtocol.sharedSecret
    secret: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkforceIntegrationEncryption"
