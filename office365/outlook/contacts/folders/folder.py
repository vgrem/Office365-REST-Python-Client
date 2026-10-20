from typing import TYPE_CHECKING, Optional

from office365.directory.extensions.extended_property import (
    MultiValueLegacyExtendedProperty,
    SingleValueLegacyExtendedProperty,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.contacts.collection import ContactCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    pass


class ContactFolder(Entity):
    """A folder that contains contacts."""

    @odata(name="contacts", navigation=True)
    @property
    def contacts(self) -> ContactCollection:
        """The contacts in the folder. Navigation property. Read-only. Nullable."""

        return self.properties.get(
            "contacts", ContactCollection(self.context, ResourcePath("contacts", self.resource_path))
        )

    @odata(name="childFolders", navigation=True)
    @property
    def child_folders(self) -> EntityCollection["ContactFolder"]:
        """The collection of child folders in the folder. Navigation property. Read-only. Nullable."""
        return self.properties.get(
            "childFolders",
            EntityCollection(self.context, ContactFolder, ResourcePath("childFolders", self.resource_path)),
        )

    @odata(name="multiValueExtendedProperties", navigation=True)
    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """The collection of multi-value extended properties defined for the Contact folder."""
        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection(
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="singleValueExtendedProperties", navigation=True)
    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """The collection of single-value extended properties defined for the Contact folder."""
        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection(
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="displayName")
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @odata(name="parentFolderId")
    @property
    def parent_folder_id(self) -> Optional[str]:
        """Gets the parentFolderId property"""
        return self.properties.get("parentFolderId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ContactFolder"
