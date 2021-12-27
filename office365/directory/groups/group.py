import json

from office365.directory.applications.app_role_assignment import AppRoleAssignmentCollection
from office365.directory.licenses.assigned_license import AssignedLicense
from office365.directory.directory_object import DirectoryObject
from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.entity_collection import EntityCollection, DeltaCollection
from office365.onedrive.drives.drive import Drive
from office365.onenote.onenote import Onenote
from office365.outlook.calendar.event import Event
from office365.planner.planner_group import PlannerGroup
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.team import Team


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    def renew(self):
        """
        Renews a group's expiration. When a group is renewed, the group expiration is extended by the number
        of days defined in the policy.
        """
        qry = ServiceOperationQuery(self, "renew")
        self.context.add_query(qry)
        return self

    def add_favorite(self):
        """Add the group to the list of the current user's favorite groups. Supported for Microsoft 365 groups only."""
        qry = ServiceOperationQuery(self, "addFavorite")
        self.context.add_query(qry)
        return self

    def remove_favorite(self):
        """
        Remove the group from the list of the current user's favorite groups. Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "removeFavorite")
        self.context.add_query(qry)
        return self

    def reset_unseen_count(self):
        """
        Reset the unseenCount of all the posts that the current user has not seen since their last visit.
        Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "resetUnseenCount")
        self.context.add_query(qry)
        return self

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

        :type group_ids: list[str]
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
        """Users and groups that are members of this group.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('members',
                                 DirectoryObjectCollection(self.context, ResourcePath("members", self.resource_path)))

    @property
    def transitive_members(self):
        """
        Get a list of the group's members. A group can have users, devices, organizational contacts,
        and other groups as members. This operation is transitive and returns a flat list of all nested members.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('transitiveMembers',
                                 DirectoryObjectCollection(self.context,
                                                           ResourcePath("transitiveMembers", self.resource_path)))

    @property
    def transitive_member_of(self):
        """
        Get groups that the group is a member of. This operation is transitive and will also include all groups that
        this groups is a nested member of. Unlike getting a user's Microsoft 365 groups, this returns all
        types of groups, not just Microsoft 365 groups.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('transitiveMemberOf',
                                 DirectoryObjectCollection(self.context,
                                                           ResourcePath("transitiveMemberOf", self.resource_path)))

    @property
    def owners(self):
        """The owners of the group.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('owners',
                                 DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)))

    @property
    def drives(self):
        """The group's drives. Read-only.

        :rtype: EntityCollection
        """
        return self.get_property('drives',
                                 EntityCollection(self.context, Drive, ResourcePath("drives", self.resource_path)))

    @property
    def sites(self):
        """The list of SharePoint sites in this group. Access the default site with /sites/root.

        :rtype: SiteCollection
        """
        from office365.onedrive.sites.sites_with_root import SitesWithRoot
        return self.get_property('sites',
                                 SitesWithRoot(self.context, ResourcePath("sites", self.resource_path)))

    @property
    def events(self):
        """Get an event collection or an event."""
        return self.properties.get('events', DeltaCollection(self.context, Event,
                                                             ResourcePath("events", self.resource_path)))

    @property
    def app_role_assignments(self):
        """Get an event collection or an appRoleAssignments."""
        return self.properties.get('appRoleAssignments',
                                   AppRoleAssignmentCollection(self.context,
                                                               ResourcePath("appRoleAssignments", self.resource_path)))

    @property
    def onenote(self):
        """Represents the Onenote services available to a group."""
        return self.properties.get('onenote',
                                   Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    @property
    def planner(self):
        """The plannerGroup resource provide access to Planner resources for a group."""
        return self.properties.get('planner',
                                   PlannerGroup(self.context, ResourcePath("planner", self.resource_path)))

    @property
    def assigned_licenses(self):
        return self.properties.get('assignedLicenses', ClientValueCollection(AssignedLicense))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "transitiveMembers": self.transitive_members,
                "transitiveMemberOf": self.transitive_member_of,
                "appRoleAssignments": self.app_role_assignments
            }
            default_value = property_mapping.get(name, None)
        return super(Group, self).get_property(name, default_value)
