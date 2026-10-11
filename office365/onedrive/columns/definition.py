from __future__ import annotations

from typing import Optional

from office365.onedrive.base_item import BaseItem
from office365.onedrive.columns.boolean import BooleanColumn
from office365.onedrive.columns.calculated import CalculatedColumn
from office365.onedrive.columns.choice import ChoiceColumn
from office365.onedrive.columns.content_approval_status import (
    ContentApprovalStatusColumn,
)
from office365.onedrive.columns.currency import CurrencyColumn
from office365.onedrive.columns.datetime import DateTimeColumn
from office365.onedrive.columns.default_value import DefaultColumnValue
from office365.onedrive.columns.geolocation import GeolocationColumn
from office365.onedrive.columns.hyperlink_or_picture import HyperlinkOrPictureColumn
from office365.onedrive.columns.lookup import LookupColumn
from office365.onedrive.columns.number import NumberColumn
from office365.onedrive.columns.person_or_group import PersonOrGroupColumn
from office365.onedrive.columns.term import TermColumn
from office365.onedrive.columns.text import TextColumn
from office365.onedrive.columns.thumbnail import ThumbnailColumn
from office365.onedrive.columns.validation import ColumnValidation
from office365.onedrive.contenttypes.info import ContentTypeInfo
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class ColumnDefinition(BaseItem):
    """
    Represents a column in a site, list, or contentType.

    ColumnDefinitions and field values for hidden columns aren't shown by default.
    To list hidden columnDefinitions, include hidden in your $select statement.
    To list hidden field values on listItems, include the desired columns by name in your $select statement.
    """

    def __str__(self) -> str:
        return self.name or ""

    def __repr__(self):
        return self.name or self.id or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The user-facing name of the column."""
        return self.properties.get("displayName", None)

    @property
    def enforce_unique_values(self) -> Optional[bool]:
        """If true, no two list items may have the same value for this column."""
        return self.properties.get("enforceUniqueValues", None)

    @property
    def indexed(self) -> Optional[bool]:
        """Specifies whether the column values can used for sorting and searching."""
        return self.properties.get("indexed", None)

    @odata(name="contentApprovalStatus")
    @property
    def content_approval_status(self) -> ContentApprovalStatusColumn:
        """This column stores content approval status."""
        return self.properties.get("contentApprovalStatus", ContentApprovalStatusColumn())

    @property
    def column_group(self) -> Optional[str]:
        """For site columns, the name of the group this column belongs to. Helps organize related columns."""
        return self.properties.get("columnGroup", None)

    @property
    def boolean(self) -> BooleanColumn:
        """This column stores boolean values."""
        return self.properties.get("boolean", BooleanColumn())

    @property
    def geolocation(self) -> GeolocationColumn:
        """This column stores a geolocation."""
        return self.properties.get("geolocation", GeolocationColumn())

    @property
    def calculated(self) -> CalculatedColumn:
        """This column's data is calculated based on other columns."""
        return self.properties.get("calculated", CalculatedColumn())

    @property
    def choice(self) -> ChoiceColumn:
        """This column stores data from a list of choices."""
        return self.properties.get("choice", ChoiceColumn())

    @property
    def currency(self) -> CurrencyColumn:
        """This column stores currency values."""
        return self.properties.get("currency", CurrencyColumn())

    @property
    def datetime(self) -> DateTimeColumn:
        """This column stores DateTime values."""
        return self.properties.get("dateTime", DateTimeColumn())

    @odata(name="personOrGroup")
    @property
    def person_or_group(self) -> PersonOrGroupColumn:
        """This column stores Person or Group values."""
        return self.properties.get("personOrGroup", PersonOrGroupColumn())

    @property
    def text(self) -> TextColumn:
        """This column stores text values."""
        return self.properties.get("text", TextColumn())

    @property
    def validation(self) -> ColumnValidation:
        """This column stores validation formula and message for the column."""
        return self.properties.get("validation", ColumnValidation())

    @property
    def number(self) -> NumberColumn:
        """This column stores number values."""
        return self.properties.get("number", NumberColumn())

    @property
    def lookup(self) -> LookupColumn:
        """This column's data is looked up from another source in the site."""
        return self.properties.get("lookup", LookupColumn())

    @odata(name="defaultValue")
    @property
    def default_value(self) -> DefaultColumnValue:
        """The default value for this column."""
        return self.properties.get("defaultValue", DefaultColumnValue())

    @odata(name="hyperlinkOrPicture")
    @property
    def hyperlink_or_picture(self) -> HyperlinkOrPictureColumn:
        """This column stores hyperlink or picture values."""
        return self.properties.get("hyperlinkOrPicture", HyperlinkOrPictureColumn())

    @property
    def hidden(self) -> Optional[bool]:
        """Specifies whether the column is displayed in the user interface."""
        return self.properties.get("hidden", None)

    @property
    def is_deletable(self) -> Optional[bool]:
        """Indicates whether this column can be deleted."""
        return self.properties.get("isDeletable", None)

    @property
    def is_reorderable(self) -> Optional[bool]:
        """Indicates whether values in the column can be reordered."""
        return self.properties.get("isReorderable", None)

    @property
    def is_sealed(self) -> Optional[bool]:
        """Specifies whether the column can be changed."""
        return self.properties.get("isSealed", None)

    @property
    def propagate_changes(self) -> Optional[bool]:
        """If 'true', changes to this column will be propagated to lists that implement the column."""
        return self.properties.get("propagateChanges", None)

    @property
    def read_only(self) -> Optional[bool]:
        """Specifies whether the column values can be modified."""
        return self.properties.get("readOnly", None)

    @property
    def thumbnail(self):
        """This column stores thumbnail values."""
        return self.properties.get("thumbnail", ThumbnailColumn())

    @odata(name="sourceColumn")
    @property
    def source_column(self) -> "ColumnDefinition":
        """The source column for the content type column."""
        return self.properties.get(
            "sourceColumn",
            ColumnDefinition(self.context, ResourcePath("sourceColumn", self.resource_path)),
        )

    @odata(name="sourceContentType")
    @property
    def source_content_type(self) -> ContentTypeInfo:
        """ContentType from which this column is inherited from. Present only in contentTypes columns response."""
        return self.properties.get("sourceContentType", ContentTypeInfo())

    @property
    def term(self) -> TermColumn:
        """This column stores taxonomy terms."""
        return self.properties.get("term", TermColumn())

    @property
    def type(self) -> Optional[str]:
        """For site columns, the type of column."""
        return self.properties.get("type", None)

    @property
    def required(self) -> Optional[bool]:
        """Gets the required property"""
        return self.properties.get("required", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ColumnDefinition"
