from __future__ import annotations

from dataclasses import dataclass

from office365.outlook.mail.attachments.type import AttachmentType
from office365.runtime.client_value import ClientValue


@dataclass
class AttachmentInfo(ClientValue):
    attachmentType: AttachmentType = AttachmentType.file
    contentType: str | None = None
    name: str | None = None
    size: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttachmentInfo"
