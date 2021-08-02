from office365.base_item import BaseItem
from office365.onedrive.choiceColumn import ChoiceColumn


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
    def choice(self):
        """This column stores data from a list of choices."""
        return self.properties.get('choice', ChoiceColumn())
