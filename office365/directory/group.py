import json

from office365.directory.appRoleAssignment import AppRoleAssignmentCollection
from office365.directory.assignedLicense import AssignedLicense
from office365.directory.directoryObject import DirectoryObject
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.entity_collection import EntityCollection
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.siteCollection import SiteCollection
from office365.outlook.calendar.event import Event
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.team import Team


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    def subscribe_by_mail(self):
        """Calling this method will enable the current user to receive email notifications for this group,
        about new posts, events, and files in that group. Supported for Microsoft 365 groups only."""
        qry = ServiceOperationQuery(self, "subscribeByMail")
        self.context.add_query(qry)
        return self

    def unsubscribe_by_mail(self):
        """Calling this method will prevent the current user from receiving email notifications for this group
        about new posts, events, and files in that group. Supported for Microsoft 365 groups only."""
        qry = ServiceOperationQuery(self, "unsubscribeByMail")
        self.context.add_query(qry)
        return self

    def check_member_groups(self, group_ids):
        """Check for membership in the specified list of groups. Returns from the list those groups of which
        the specified group has a direct or transitive membership.

        You can check up to a maximum of 20 groups per request. This function supports Microsoft 365 and other types
        of groups provisioned in Azure AD. Note that Microsoft 365 groups cannot contain groups.
        So membership in a Microsoft 365 group is always direct.

        :type group_ids: list
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "checkMemberGroups", None, group_ids, None, result)
        self.context.add_query(qry)
        return result

    def add_team(self):
        """Create a new team under a group."""
        team = Team(self.context, ResourcePath("team", self.resource_path))
        team._parent_collection = self.parent_collection
        qry = ServiceOperationQuery(self, "team", None, team, None, team)
        self.context.add_query(qry)

        def _construct_create_team_request(request):
            cur_qry = self.context.current_query
            if cur_qry.id == qry.id:
                request.method = HttpMethod.Put
                request.set_header('Content-Type', "application/json")
                request.data = json.dumps(request.data)

        self.context.before_execute(_construct_create_team_request, False)
        return team

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the group from directory
        :type permanent_delete: bool

        """
        super(Group, self).delete_object()
        if permanent_delete:
            deleted_item = self.context.directory.deleted_groups[self.id]
            deleted_item.delete_object()
        return self

    @property
    def members(self):
        """Users and groups that are members of this group."""
        return self.properties.get('members',
                                   DirectoryObjectCollection(self.context, ResourcePath("members", self.resource_path)))

    @property
    def owners(self):
        """The owners of the group."""
        return self.properties.get('owners',
                                   DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)))

    @property
    def drives(self):
        """The group's drives. Read-only."""
        return self.properties.get('drives',
                                   DriveCollection(self.context, ResourcePath("drives", self.resource_path)))

    @property
    def sites(self):
        """The list of SharePoint sites in this group. Access the default site with /sites/root."""
        return self.properties.get('sites',
                                   SiteCollection(self.context, ResourcePath("sites", self.resource_path)))

    @property
    def events(self):
        """Get an event collection or an event."""
        return self.properties.get('events', EntityCollection(self.context, Event,
                                                              ResourcePath("events", self.resource_path)))

    @property
    def app_role_assignments(self):
        """Get an event collection or an appRoleAssignments."""
        return self.properties.get('appRoleAssignments',
                                   AppRoleAssignmentCollection(self.context,
                                                               ResourcePath("appRoleAssignments", self.resource_path)))

    @property
    def assigned_licenses(self):
        return self.properties.get('assignedLicenses',
                                   ClientValueCollection(AssignedLicense))
