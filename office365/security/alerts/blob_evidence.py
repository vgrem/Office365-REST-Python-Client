from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.alerts.blob_container_evidence import BlobContainerEvidence
from office365.security.file_hash import FileHash


@dataclass
class BlobEvidence(ClientValue):
    blobContainer: BlobContainerEvidence = field(default_factory=BlobContainerEvidence)
    etag: str | None = None
    fileHashes: ClientValueCollection[FileHash] = field(default_factory=lambda: ClientValueCollection(FileHash))
    name: str | None = None
    url: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.BlobEvidence"
