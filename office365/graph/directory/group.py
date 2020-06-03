import json

from office365.graph.directory.directoryObject import DirectoryObject
from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.onedrive.driveCollection import DriveCollection
from office365.graph.onedrive.siteCollection import SiteCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.graph.teams.team import Team


def _delete_group_from_directory(target_group):
    """
    Deletes the group from directory

    :type target_group: Group
    """
    deleted_item = target_group.context.directory.deletedGroups[target_group.id]
    deleted_item.delete_object()


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    def add_team(self):
        """Create a new team under a group."""
        team = Team(self.context)
        team._parent_collection = self.parent_collection
        qry = ServiceOperationQuery(self, "team", None, team, None, team)
        self.context.add_query(qry)
        self.context.get_pending_request().beforeExecute += self._construct_create_team_request
        return team

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the group from directory
        :type permanent_delete: bool

        """
        super(Group, self).delete_object()
        if permanent_delete:
            self.ensure_property("id", _delete_group_from_directory)

    def _construct_create_team_request(self, request):
        request.method = HttpMethod.Put
        request.set_header('Content-Type', "application/json")
        request.data = json.dumps(request.data)
        self.context.get_pending_request().beforeExecute -= self._construct_create_team_request

    @property
    def members(self):
        """Users and groups that are members of this group."""
        if self.is_property_available('members'):
            return self.properties['members']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePath("members", self.resource_path))

    @property
    def owners(self):
        """The owners of the group."""
        if self.is_property_available('owners'):
            return self.properties['owners']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePath("owners", self.resource_path))

    @property
    def drives(self):
        """The group's drives. Read-only."""
        if self.is_property_available('drives'):
            return self.properties['drives']
        else:
            return DriveCollection(self.context, ResourcePath("drives", self.resource_path))

    @property
    def sites(self):
        """The list of SharePoint sites in this group. Access the default site with /sites/root."""
        if self.is_property_available('sites'):
            return self.properties['sites']
        else:
            return SiteCollection(self.context,
                                  ResourcePath("sites", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(Group, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(
                    value,
                    self._parent_collection.resource_path)
