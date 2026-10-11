from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class SensorDeploymentPackage(ClientValue):
    downloadUrl: str | None = None
    version: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SensorDeploymentPackage"
