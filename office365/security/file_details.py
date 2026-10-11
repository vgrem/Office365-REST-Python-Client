from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class FileDetails(ClientValue):
    fileName: str | None = None
    filePath: str | None = None
    filePublisher: str | None = None
    fileSize: int | None = None
    issuer: str | None = None
    md5: str | None = None
    sha1: str | None = None
    sha256: str | None = None
    sha256Ac: str | None = None
    signer: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.FileDetails"
