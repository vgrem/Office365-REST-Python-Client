from __future__ import annotations

from datetime import datetime
from typing import IO, AnyStr, Optional

from typing_extensions import Self

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata


class Attachment(Entity):
    """A file or item (contact, event or message) attached to an event or message."""

    def __repr__(self) -> str:
        return self.name or self.id or ""

    def download(self, file_object: IO) -> Self:
        """Downloads raw contents of a file or item attachment"""

        def _save_content(return_type: ClientResult[AnyStr]) -> None:
            file_object.write(return_type.value)

        self.get_content().after_execute(_save_content)
        return self

    @require_permission(delegated=["Mail.Read"], application=["Mail.Read"])
    def get_content(self) -> ClientResult[bytes]:
        """Gets the raw contents of a file or item attachment"""
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "$value", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def name(self) -> Optional[str]:
        """The attachment's file name."""
        return self.properties.get("name", None)

    @name.setter
    def name(self, value: str) -> None:
        """Sets the attachment's file name."""
        self.set_property("name", value)

    @property
    def content_type(self) -> Optional[str]:
        return self.properties.get("contentType", None)

    @content_type.setter
    def content_type(self, value: str) -> None:
        self.set_property("contentType", value)

    @property
    def size(self) -> Optional[int]:
        return self.properties.get("size", None)

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_datetime(self) -> Optional[datetime]:
        """The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def is_inline(self) -> Optional[bool]:
        """Gets the isInline property"""
        return self.properties.get("isInline", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Attachment"
