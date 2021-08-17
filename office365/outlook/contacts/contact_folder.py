from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.resource_path import ResourcePath


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
