from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class FontPackage(Entity):
    """Represents a font package."""

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def is_hidden(self) -> Optional[bool]:
        """Gets the IsHidden property"""
        return self.properties.get("IsHidden", None)

    @property
    def is_valid(self) -> Optional[bool]:
        """Gets the IsValid property"""
        return self.properties.get("IsValid", None)

    @property
    def missing_font_files(self) -> Optional[str]:
        """Gets the MissingFontFiles property"""
        return self.properties.get("MissingFontFiles", None)

    @property
    def package_json(self) -> Optional[str]:
        """Gets the PackageJson property"""
        return self.properties.get("PackageJson", None)

    @property
    def store(self) -> Optional[int]:
        """Gets the Store property"""
        return self.properties.get("Store", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    def apply(self) -> Self:
        """Apply operation."""
        qry = ServiceOperationQuery(self, "Apply", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def delete(self) -> Self:
        """Delete operation."""
        qry = ServiceOperationQuery(self, "Delete", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def font_stream(self, font_family: str) -> ClientResult[bytes]:
        """FontStream operation.

        Args:
            font_family (str):
                fontFamily parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "FontStream", [font_family], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type
