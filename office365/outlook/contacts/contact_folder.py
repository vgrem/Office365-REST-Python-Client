from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class ContactFolder(Entity):
    """A folder that contains contacts."""

    @property
    def contacts(self):
        """The contacts in the folder. Navigation property. Read-only. Nullable."""
        from office365.outlook.contacts.contact import Contact
        return self.properties.get('contacts',
                                   EntityCollection(self.context, Contact,
                                                    ResourcePath("contacts", self.resource_path)))

    @property
    def child_folders(self):
        """The collection of child folders in the folder. Navigation property. Read-only. Nullable."""
        return self.properties.get('childFolders',
                                   EntityCollection(self.context, ContactFolder,
                                                    ResourcePath("childFolders", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "childFolders": self.child_folders
            }
            default_value = property_mapping.get(name, None)
        return super(ContactFolder, self).get_property(name, default_value)
