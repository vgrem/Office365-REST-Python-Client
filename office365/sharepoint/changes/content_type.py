from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.changes.change import Change


class ChangeContentType(Change):
    """Specifies a change on a content type."""

    @property
    def content_type_id(self) -> Optional[str]:
        """Identifies the content type that has changed."""
        return self.properties.get("ContentTypeId", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)
