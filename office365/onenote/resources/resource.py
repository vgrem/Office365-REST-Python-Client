from __future__ import annotations

from typing import Optional

from office365.directory.permissions.require_permission import require_permission
from office365.onenote.entity_base_model import OnenoteEntityBaseModel
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery


class OnenoteResource(OnenoteEntityBaseModel):
    """An image or other file resource on a OneNote page."""

    @require_permission(
        delegated=["Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All"],
        application=["Notes.Read.All", "Notes.ReadWrite.All"],
    )
    def get_content(self) -> ClientResult[bytes]:
        """Retrieve the binary data of a file or image resource object."""
        return_type = ClientResult(self.context)
        qry = FunctionQuery(self, "content", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def content_url(self) -> Optional[str]:
        """The URL for downloading the content"""
        return self.properties.get("contentUrl", None)

    @property
    def content(self) -> Optional[bytes]:
        """Gets the content property"""
        return self.properties.get("content", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnenoteResource"
