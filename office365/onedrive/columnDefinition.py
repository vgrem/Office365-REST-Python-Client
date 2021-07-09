from office365.base_item import BaseItem
from office365.onedrive.choiceColumn import ChoiceColumn


class ColumnDefinition(BaseItem):

    @property
    def column_group(self):
        return self.properties.get('columnGroup', None)

    @property
    def choice(self):
        return self.properties.get('choice', ChoiceColumn())
