from office365.directory.directoryObject import DirectoryObject
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.siteCollection import SiteCollection
from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path_entity import ResourcePathEntity


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    def delete_object(self):
        """Deletes the group."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def members(self):
        """Users and groups that are members of this group."""
        if self.is_property_available('members'):
            return self.properties['members']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePathEntity(self.context, self.resourcePath, "members"))

    @property
    def owners(self):
        """The owners of the group."""
        if self.is_property_available('owners'):
            return self.properties['owners']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePathEntity(self.context, self.resourcePath, "owners"))

    @property
    def drives(self):
        """The group's drives. Read-only."""
        if self.is_property_available('drives'):
            return self.properties['drives']
        else:
            return DriveCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "drives"))

    @property
    def sites(self):
        """The list of SharePoint sites in this group. Access the default site with /sites/root."""
        if self.is_property_available('sites'):
            return self.properties['sites']
        else:
            return SiteCollection(self.context,
                                  ResourcePathEntity(self.context, self.resourcePath, "sites"))

    def set_property(self, name, value, serializable=True):
        super(Group, self).set_property(name, value, serializable)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePathEntity(
                    self.context,
                    self._parent_collection.resourcePath,
                    value)
