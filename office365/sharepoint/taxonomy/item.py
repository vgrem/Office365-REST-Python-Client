from office365.runtime.client_object import ClientObject
from office365.runtime.paths.resource_path import ResourcePath


class TaxonomyItem(ClientObject):
    """The TaxonomyItem class is a base class that represents an item in the TermStore (section 3.1.5.23).
    A TaxonomyItem has a name and a unique identifier. It also contains date and time of when the item is created and
    when the item is last modified."""

    @property
    def id(self):
        """Gets the Id of the current TaxonomyItem

        :rtype: str
        """
        return self.properties.get("id", None)

    @property
    def name(self):
        """Gets the name of the current TaxonomyItem object

        :rtype: str
        """
        return self.properties.get("name", None)

    @property
    def property_ref_name(self):
        return "id"

    def set_property(self, name, value, persist_changes=True):
        super(TaxonomyItem, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == self.property_ref_name:
                self._resource_path = ResourcePath(value, self.parent_collection.resource_path)
        return self


