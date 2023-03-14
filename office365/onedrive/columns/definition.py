from office365.base_item import BaseItem
from office365.onedrive.columns.boolean import BooleanColumn
from office365.onedrive.columns.calculated import CalculatedColumn
from office365.onedrive.columns.choice import ChoiceColumn
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


class ColumnDefinition(BaseItem):
    """
    Represents a column in a site, list, or contentType.

    ColumnDefinitions and field values for hidden columns aren't shown by default.
    To list hidden columnDefinitions, include hidden in your $select statement.
    To list hidden field values on listItems, include the desired columns by name in your $select statement.
    """

    @property
    def display_name(self):
        """The user-facing name of the column.

        :rtype: str or None
        """
        return self.properties.get("displayName", None)

    @property
    def enforce_unique_values(self):
        """
        If true, no two list items may have the same value for this column.

        :rtype: bool or None
        """
        return self.properties.get('enforceUniqueValues', None)

    @property
    def indexed(self):
        """Specifies whether the column values can used for sorting and searching."""
        return self.properties.get('indexed', None)

    @property
    def column_group(self):
        """For site columns, the name of the group this column belongs to. Helps organize related columns."""
        return self.properties.get('columnGroup', None)

    @property
    def boolean(self):
        """This column stores boolean values."""
        return self.properties.get('boolean', BooleanColumn())

    @property
    def geolocation(self):
        """This column stores a geolocation."""
        return self.properties.get('geolocation', GeolocationColumn())

    @property
    def calculated(self):
        """This column's data is calculated based on other columns."""
        return self.properties.get('calculated', CalculatedColumn())

    @property
    def choice(self):
        """This column stores data from a list of choices."""
        return self.properties.get('choice', ChoiceColumn())

    @property
    def person_or_group(self):
        """This column stores Person or Group values."""
        return self.properties.get('personOrGroup', PersonOrGroupColumn())

    @property
    def text(self):
        """This column stores text values."""
        return self.properties.get('text', TextColumn())

    @property
    def validation(self):
        """This column stores validation formula and message for the column."""
        return self.properties.get('validation', ColumnValidation())

    @property
    def number(self):
        """This column stores number values."""
        return self.properties.get('number', NumberColumn())

    @property
    def lookup(self):
        """This column's data is looked up from another source in the site."""
        return self.properties.get('lookup', LookupColumn())

    @property
    def default_value(self):
        """The default value for this column."""
        return self.properties.get('defaultValue', DefaultColumnValue())

    @property
    def hyperlink_or_picture(self):
        """This column stores hyperlink or picture values."""
        return self.properties.get('hyperlinkOrPicture', HyperlinkOrPictureColumn())

    @property
    def is_deletable(self):
        """Indicates whether this column can be deleted.

        :rtype: bool or None
        """
        return self.properties.get('isDeletable', None)

    @property
    def is_sealed(self):
        """Specifies whether the column can be changed.

        :rtype: bool or None
        """
        return self.properties.get('isSealed', None)

    @property
    def propagate_changes(self):
        """If 'true', changes to this column will be propagated to lists that implement the column.

        :rtype: bool or None
        """
        return self.properties.get('propagateChanges', None)

    @property
    def thumbnail(self):
        """This column stores thumbnail values."""
        return self.properties.get('thumbnail', ThumbnailColumn())

    @property
    def source_column(self):
        """The source column for the content type column."""
        return self.properties.get('sourceColumn', ColumnDefinition(self.context, ResourcePath(self.resource_path)))

    @property
    def source_content_type(self):
        """ContentType from which this column is inherited from. Present only in contentTypes columns response."""
        return self.properties.get('sourceContentType', ContentTypeInfo())

    @property
    def term(self):
        """This column stores taxonomy terms."""
        return self.properties.get('term', TermColumn())

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "defaultValue": self.default_value,
                "hyperlinkOrPicture": self.hyperlink_or_picture,
                "personOrGroup": self.person_or_group,
                "sourceColumn": self.source_column,
                "sourceContentType": self.source_content_type
            }
            default_value = property_mapping.get(name, None)
        return super(ColumnDefinition, self).get_property(name, default_value)

