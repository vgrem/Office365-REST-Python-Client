from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class MacOSLobChildApp(ClientValue):
    buildNumber: str | None = None
    bundleId: str | None = None
    versionNumber: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSLobChildApp"
