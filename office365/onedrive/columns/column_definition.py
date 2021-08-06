from office365.base_item import BaseItem
from office365.onedrive.columns.calculated_column import CalculatedColumn
from office365.onedrive.columns.choice_column import ChoiceColumn
from office365.onedrive.columns.default_column_value import DefaultColumnValue


class ColumnDefinition(BaseItem):

    @property
    def indexed(self):
        """Specifies whether the column values can used for sorting and searching."""
        return self.properties.get('indexed', None)

    @property
    def column_group(self):
        """For site columns, the name of the group this column belongs to. Helps organize related columns."""
        return self.properties.get('columnGroup', None)

    @property
    def calculated(self):
        """This column's data is calculated based on other columns."""
        return self.get_property('calculated', CalculatedColumn())

    @property
    def choice(self):
        """This column stores data from a list of choices."""
        return self.get_property('choice', ChoiceColumn())

    @property
    def default_value(self):
        """The default value for this column."""
        return self.get_property('defaultValue', DefaultColumnValue())
