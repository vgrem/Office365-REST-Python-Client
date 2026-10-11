from __future__ import annotations

from typing import Any, Optional, cast

from office365.outlook.mail.attachments.attachment import Attachment


class FileAttachment(Attachment):
    """A file (such as a text file or Word document) attached to a user event, message, or post."""

    def to_json(self, json_format: Any = None) -> dict:
        # ``attachment`` is an abstract type: Graph needs the concrete
        # discriminator on create, and the V4 format does not add it.
        result: dict = cast(dict, super().to_json(json_format))
        result["@odata.type"] = f"#{self.entity_type_name}"
        return result

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.fileAttachment"

    @property
    def content_id(self) -> Optional[str]:
        """The ID of the attachment in the Exchange store."""
        return self.properties.get("contentId", None)

    @property
    def content_location(self) -> Optional[str]:
        """ """
        return self.properties.get("content_location", None)

    @property
    def content_bytes(self) -> Optional[bytes]:
        """The base64-encoded contents of the file."""
        return self.properties.get("contentBytes", None)

    @content_bytes.setter
    def content_bytes(self, value: str | bytes) -> None:
        """Sets the base64-encoded contents of the file."""
        self.set_property("contentBytes", value.decode("utf-8") if isinstance(value, bytes) else value)
