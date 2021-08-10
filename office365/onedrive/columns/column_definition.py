from office365.base_item import BaseItem
from office365.onedrive.columns.calculated_column import CalculatedColumn
from office365.onedrive.columns.choice_column import ChoiceColumn
from office365.onedrive.columns.default_column_value import DefaultColumnValue
from office365.onedrive.columns.geolocation_column import GeolocationColumn
from office365.onedrive.columns.lookup_column import LookupColumn
from office365.onedrive.columns.number_column import NumberColumn
from office365.onedrive.columns.person_or_group_column import PersonOrGroupColumn
from office365.onedrive.columns.text_column import TextColumn


class ColumnDefinition(BaseItem):

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
    def geolocation(self):
        """This column stores a geolocation."""
        return self.get_property('geolocation', GeolocationColumn())

    @property
    def calculated(self):
        """This column's data is calculated based on other columns."""
        return self.get_property('calculated', CalculatedColumn())

    @property
    def choice(self):
        """This column stores data from a list of choices."""
        return self.get_property('choice', ChoiceColumn())

    @property
    def person_or_group(self):
        """This column stores Person or Group values."""
        return self.get_property('personOrGroup', PersonOrGroupColumn())

    @property
    def text(self):
        """This column stores text values."""
        return self.get_property('text', TextColumn())

    @property
    def number(self):
        """This column stores number values."""
        return self.get_property('number', NumberColumn())

    @property
    def lookup(self):
        """This column's data is looked up from another source in the site."""
        return self.get_property('lookup', LookupColumn())

    @property
    def default_value(self):
        """The default value for this column."""
        return self.get_property('defaultValue', DefaultColumnValue())
