from office365.entity_collection import EntityCollection
from office365.onedrive.listitems.field_value_set import FieldValueSet
from office365.onedrive.versions.base_item_version import BaseItemVersion
from office365.runtime.resource_path import ResourcePath


class ListItemVersion(BaseItemVersion):
    """The listItemVersion resource represents a previous version of a ListItem resource."""

    @property
    def fields(self):
        """A collection of the fields and values for this version of the list item.

        :rtype: EntityCollection
        """
        return self.get_property('fields',
                                 EntityCollection(self.context, FieldValueSet,
                                                  ResourcePath("fields", self.resource_path)))
