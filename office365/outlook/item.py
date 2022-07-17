from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class OutlookItem(Entity):

    @property
    def change_key(self):
        """Identifies the version of the item. Every time the item is changed, changeKey changes as well.
        This allows Exchange to apply changes to the correct version of the object. """
        return self.properties.get('ChangeKey', None)

    @property
    def categories(self):
        """
        The categories associated with the item
        """
        return self.properties.get("categories", StringCollection())


