from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.json_format import JsonProfile


@dataclass
class ChatMessageBody(ClientValue):
    """The plain-text or rich-text content of a chat/channel message.

    Teams messages expect a ``chatMessageBody`` payload but reject an explicit
    OData type marker for it, so :meth:`to_json` emits the fields without the
    type metadata and lets the service infer the type.
    """

    content: str | None = None
    contentType: str | None = None

    def to_json(self, profile: JsonProfile | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.content is not None:
            result["content"] = self.content
        if self.contentType is not None:
            result["contentType"] = self.contentType
        return result

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Teams.GraphSvc.chatMessageBody"
