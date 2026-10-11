from __future__ import annotations

from dataclasses import dataclass, field

from office365.outlook.mail.tips.error import MailTipsError
from office365.runtime.client_value import ClientValue
from office365.security.stream import Stream


@dataclass
class ExportItemResponse(ClientValue):
    changeKey: str | None = None
    data: Stream = field(default_factory=Stream)
    error: MailTipsError = field(default_factory=MailTipsError)
    itemId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExportItemResponse"
