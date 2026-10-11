from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.directory.applications.roles.assignment_collection import (
    AppRoleAssignmentCollection,
)
from office365.directory.extensions.extension import Extension
from office365.directory.groups.assigned_label import AssignedLabel
from office365.directory.groups.lifecycle_policy import GroupLifecyclePolicy
from office365.directory.groups.on_premises_sync_behavior import OnPremisesSyncBehavior
from office365.directory.groups.setting import GroupSetting
from office365.directory.licenses.assigned_license import AssignedLicense
from office365.directory.licenses.processing_state import LicenseProcessingState
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.object import DirectoryObject
from office365.directory.objects.onpremisesprovisioningerror import (
    OnPremisesProvisioningError,
)
from office365.directory.objects.serviceprovisioningerror import (
    ServiceProvisioningError,
)
from office365.directory.permissions.grants.resource_specific import (
    ResourceSpecificPermissionGrant,
)
from office365.directory.permissions.require_permission import require_permission
from office365.directory.profile_photo import ProfilePhoto
from office365.entity_collection import EntityCollection
from office365.onedrive.drives.drive import Drive
from office365.onenote.onenote import Onenote
from office365.outlook.calendar.calendar import Calendar
from office365.outlook.calendar.events.collection import EventCollection
from office365.outlook.calendar.events.event import Event
from office365.outlook.mail.conversation import Conversation
from office365.outlook.mail.conversation_thread import ConversationThread
from office365.planner.group import PlannerGroup
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.teams.team import Team

if TYPE_CHECKING:
    from office365.directory.groups.access_type import GroupAccessType
    from office365.directory.users.onpremisesextensionattributes import (
        OnPremisesExtensionAttributes,
    )


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    def __repr__(self):
        return self.display_name or self.id or self.entity_type_name

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def renew(self) -> Self:
        """
        Renews a group's expiration. When a group is renewed, the group expiration is extended by the number
        of days defined in the policy.
        """
        qry = ServiceOperationQuery(self, "renew")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def add_favorite(self) -> Self:
        """Add the group to the list of the current user's favorite groups. Supported for Microsoft 365 groups only."""
        qry = ServiceOperationQuery(self, "addFavorite")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Group.Read.All", "Group.ReadWrite.All"], application=["Group.Read.All", "Group.ReadWrite.All"]
    )
    def check_granted_permissions_for_app(self) -> EntityCollection[ResourceSpecificPermissionGrant]:
        """"""
        return_type = EntityCollection(self.context, ResourceSpecificPermissionGrant)
        qry = ServiceOperationQuery(self, "checkGrantedPermissionsForApp", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def remove_favorite(self) -> Self:
        """
        Remove the group from the list of the current user's favorite groups. Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "removeFavorite")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def reset_unseen_count(self) -> Self:
        """
        Reset the unseenCount of all the posts that the current user has not seen since their last visit.
        Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "resetUnseenCount")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def subscribe_by_mail(self) -> Self:
        """Calling this method will enable the current user to receive email notifications for this group,
        about new posts, events, and files in that group. Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "subscribeByMail")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def unsubscribe_by_mail(self) -> Self:
        """Calling this method will prevent the current user from receiving email notifications for this group
        about new posts, events, and files in that group. Supported for Microsoft 365 groups only.
        """
        qry = ServiceOperationQuery(self, "unsubscribeByMail")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Group.ReadWrite.All", "Team.Create"], application=["Group.ReadWrite.All", "Team.Create"]
    )
    def add_team(self) -> Team:
        """Create a new team under a group."""
        qry = ServiceOperationQuery(self, "team", None, self.team, None, self.team)

        def _construct_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Put
            request.set_header("Content-Type", "application/json")
            request.data = json.dumps(request.data)

        self.context.add_query(qry).before_execute(_construct_request, once=False)
        return self.team

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def delete_object(self, permanent_delete: bool = False, *, ignore_missing: bool = False) -> Self:
        """Args:
        permanent_delete (bool): Permanently deletes the group from directory
        ignore_missing (bool): Treat deleting a missing group as success
        """
        super().delete_object(ignore_missing=ignore_missing)
        deleted_group = DirectoryObject(
            self.context, EntityPath(self.id, self.context.directory.deleted_groups.resource_path)
        )
        self.context.directory.deleted_groups.add_child(deleted_group)
        if permanent_delete:
            deleted_group.delete_object(ignore_missing=ignore_missing)
        return self

    @odata(name="assignedLabels")
    @property
    def assigned_labels(self) -> ClientValueCollection[AssignedLabel]:
        """The list of sensitivity label pairs (label ID, label name) associated with a Microsoft 365 group."""
        return self.properties.get("assignedLabels", ClientValueCollection(AssignedLabel))

    @property
    def classification(self) -> Optional[str]:
        """Describes a classification for the group (such as low, medium or high business impact). Valid values for
        this property are defined by creating a ClassificationList setting value, based on the template definition.
        """
        return self.properties.get("classification", None)

    @property
    def display_name(self) -> Optional[str]:
        """
        The display name for the group. This property is required when a group is created and cannot be cleared during
        updates. Maximum length is 256 characters.

        Returned by default. Supports $filter (eq, ne, not, ge, le, in, startsWith, and eq on null values), $search,
        and $orderby.
        """
        return self.properties.get("displayName", None)

    @odata(name="groupTypes")
    @property
    def group_types(self) -> StringCollection:
        """
        Specifies the group type and its membership.

        If the collection contains Unified, the group is a Microsoft 365 group; otherwise, it's either a security group
        or distribution group. For details, see groups overview.

        If the collection includes DynamicMembership, the group has dynamic membership; otherwise, membership is static.

        Returned by default. Supports $filter (eq, not).
        """
        return self.properties.get("groupTypes", StringCollection())

    @property
    def has_members_with_license_errors(self) -> Optional[bool]:
        """
        Indicates whether there are members in this group that have license errors from its group-based license
        assignment.

        This property is never returned on a GET operation. You can use it as a $filter argument to get groups that
        have members with license errors (that is, filter for this property being true)
        """
        return self.properties.get("hasMembersWithLicenseErrors", None)

    @property
    def is_assignable_to_role(self) -> Optional[bool]:
        """
        Indicates whether this group can be assigned to an Azure Active Directory role or not. Optional.

        This property can only be set while creating the group and is immutable. If set to true, the securityEnabled
        property must also be set to true, visibility must be Hidden, and the group cannot be a dynamic group
        (that is, groupTypes cannot contain DynamicMembership).

        Only callers in Global Administrator and Privileged Role Administrator roles can set this property.
        The caller must also be assigned the RoleManagement.ReadWrite.Directory permission to set this property or
        update the membership of such groups. For more, see Using a group to manage Azure AD role assignments
        """
        return self.properties.get("isAssignableToRole", None)

    @odata(name="licenseProcessingState")
    @property
    def license_processing_state(self) -> LicenseProcessingState:
        """Indicates status of the group license assignment to all members of the group. Default value is false.
        Read-only. Possible values: QueuedForProcessing, ProcessingInProgress, and ProcessingComplete.
        """
        return self.properties.get("licenseProcessingState", LicenseProcessingState())

    @property
    def mail(self) -> Optional[str]:
        """
        The SMTP address for the group, for example, "serviceadmins@contoso.onmicrosoft.com".
        """
        return self.properties.get("mail", None)

    @property
    def mail_enabled(self) -> Optional[bool]:
        """
        Specifies whether the group is mail-enabled. Required.
        """
        return self.properties.get("mailEnabled", None)

    @property
    def mail_nickname(self) -> Optional[str]:
        """
        The mail alias for the group, unique for Microsoft 365 groups in the organization. Maximum length is 64
        characters.
        """
        return self.properties.get("mailNickname", None)

    @property
    def on_premises_domain_name(self) -> Optional[str]:
        return self.properties.get("onPremisesDomainName", None)

    @property
    def conversations(self) -> EntityCollection[Conversation]:
        """The group's conversations."""
        return self.properties.get(
            "conversations",
            EntityCollection(self.context, Conversation, ResourcePath("conversations", self.resource_path)),
        )

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> Optional[datetime]:
        """Timestamp of when the group was created (``None`` when absent)."""
        return self.properties.get("createdDateTime")

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """
        The collection of open extensions defined for the group
        """
        return self.properties.get(
            "extensions", EntityCollection(self.context, Extension, ResourcePath("extensions", self.resource_path))
        )

    @property
    def members(self) -> DirectoryObjectCollection:
        """Users and groups that are members of this group."""
        return self.properties.get(
            "members", DirectoryObjectCollection(self.context, ResourcePath("members", self.resource_path))
        )

    @odata(name="rejectedSenders")
    @property
    def rejected_senders(self) -> DirectoryObjectCollection:
        """
        The list of users or groups not allowed to create posts or calendar events in this group. Nullable
        """
        return self.properties.get(
            "rejectedSenders",
            DirectoryObjectCollection(self.context, ResourcePath("rejectedSenders", self.resource_path)),
        )

    @odata(name="transitiveMembers")
    @property
    def transitive_members(self) -> DirectoryObjectCollection:
        """
        Get a list of the group's members. A group can have members, devices, organizational contacts,
        and other groups as members. This operation is transitive and returns a flat list of all nested members.
        """
        return self.properties.get(
            "transitiveMembers",
            DirectoryObjectCollection(self.context, ResourcePath("transitiveMembers", self.resource_path)),
        )

    @odata(name="transitiveMemberOf")
    @property
    def transitive_member_of(self) -> DirectoryObjectCollection:
        """
        Get groups that the group is a member of. This operation is transitive and will also include all groups that
        this groups is a nested member of. Unlike getting a user's Microsoft 365 groups, this returns all
        types of groups, not just Microsoft 365 groups.
        """
        return self.properties.get(
            "transitiveMemberOf",
            DirectoryObjectCollection(self.context, ResourcePath("transitiveMemberOf", self.resource_path)),
        )

    @property
    def threads(self) -> EntityCollection[ConversationThread]:
        """The group's conversation threads"""
        return self.properties.get(
            "threads", EntityCollection(self.context, ConversationThread, ResourcePath("threads", self.resource_path))
        )

    @property
    def owners(self) -> DirectoryObjectCollection:
        """The owners of the group."""
        return self.properties.get(
            "owners", DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path))
        )

    @property
    def drives(self) -> EntityCollection[Drive]:
        """
        The group's drives. Read-only.
        """
        return self.properties.get(
            "drives", EntityCollection(self.context, Drive, ResourcePath("drives", self.resource_path), self)
        )

    @property
    def sites(self):
        """
        The list of SharePoint sites in this group. Access the default site with /sites/root.
        """
        from office365.onedrive.sites.sites_with_root import SitesWithRoot

        return self.properties.get("sites", SitesWithRoot(self.context, ResourcePath("sites", self.resource_path)))

    @property
    def events(self) -> EventCollection:
        """Get an event collection or an event."""
        return self.properties.get("events", EventCollection(self.context, ResourcePath("events", self.resource_path)))

    @odata(name="appRoleAssignments")
    @property
    def app_role_assignments(self) -> AppRoleAssignmentCollection:
        """Get an event collection or an appRoleAssignments."""
        return self.properties.get(
            "appRoleAssignments",
            AppRoleAssignmentCollection(self.context, ResourcePath("appRoleAssignments", self.resource_path)),
        )

    @property
    def onenote(self) -> Onenote:
        """Represents the Onenote services available to a group."""
        return self.properties.get("onenote", Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    @property
    def planner(self) -> PlannerGroup:
        """The plannerGroup resource provide access to Planner resources for a group."""
        return self.properties.get("planner", PlannerGroup(self.context, ResourcePath("planner", self.resource_path)))

    @odata(name="permissionGrants")
    @property
    def permission_grants(self) -> EntityCollection[ResourceSpecificPermissionGrant]:
        """List permissions that have been granted to apps to access the group."""
        return self.properties.setdefault(
            "permissionGrants",
            EntityCollection(self.context, ResourceSpecificPermissionGrant, ResourcePath("permissionGrants")),
        )

    @property
    def photo(self) -> ProfilePhoto:
        """The group's profile photo"""
        return self.properties.get("photo", ProfilePhoto(self.context, ResourcePath("photo", self.resource_path)))

    @property
    def team(self) -> Team:
        """The team associated with this group."""
        return self.properties.setdefault("team", Team(self.context, ResourcePath(self.id, ResourcePath("teams"))))

    @odata(name="assignedLicenses")
    @property
    def assigned_licenses(self) -> ClientValueCollection[AssignedLicense]:
        """
        The licenses that are assigned to the group.
        Returned only on $select. Supports $filter (eq).Read-only.
        """
        return self.properties.get("assignedLicenses", ClientValueCollection(AssignedLicense))

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def expiration_date_time(self) -> datetime:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def info_catalogs(self) -> StringCollection:
        """Gets the infoCatalogs property"""
        return self.properties.get("infoCatalogs", StringCollection(None))

    @property
    def is_management_restricted(self) -> Optional[bool]:
        """Gets the isManagementRestricted property"""
        return self.properties.get("isManagementRestricted", None)

    @property
    def membership_rule(self) -> Optional[str]:
        """Gets the membershipRule property"""
        return self.properties.get("membershipRule", None)

    @property
    def membership_rule_processing_state(self) -> Optional[str]:
        """Gets the membershipRuleProcessingState property"""
        return self.properties.get("membershipRuleProcessingState", None)

    @property
    def on_premises_last_sync_date_time(self) -> datetime:
        """Gets the onPremisesLastSyncDateTime property"""
        return self.properties.get("onPremisesLastSyncDateTime", datetime.min)

    @property
    def on_premises_net_bios_name(self) -> Optional[str]:
        """Gets the onPremisesNetBiosName property"""
        return self.properties.get("onPremisesNetBiosName", None)

    @odata(name="onPremisesProvisioningErrors")
    @property
    def on_premises_provisioning_errors(self) -> ClientValueCollection[OnPremisesProvisioningError]:
        """Gets the onPremisesProvisioningErrors property"""
        return self.properties.get(
            "onPremisesProvisioningErrors",
            ClientValueCollection[OnPremisesProvisioningError](OnPremisesProvisioningError),
        )

    @property
    def on_premises_sam_account_name(self) -> Optional[str]:
        """Gets the onPremisesSamAccountName property"""
        return self.properties.get("onPremisesSamAccountName", None)

    @property
    def on_premises_security_identifier(self) -> Optional[str]:
        """Gets the onPremisesSecurityIdentifier property"""
        return self.properties.get("onPremisesSecurityIdentifier", None)

    @property
    def on_premises_sync_enabled(self) -> Optional[bool]:
        """Gets the onPremisesSyncEnabled property"""
        return self.properties.get("onPremisesSyncEnabled", None)

    @property
    def preferred_data_location(self) -> Optional[str]:
        """Gets the preferredDataLocation property"""
        return self.properties.get("preferredDataLocation", None)

    @property
    def preferred_language(self) -> Optional[str]:
        """Gets the preferredLanguage property"""
        return self.properties.get("preferredLanguage", None)

    @property
    def proxy_addresses(self) -> StringCollection:
        """Gets the proxyAddresses property"""
        return self.properties.get("proxyAddresses", StringCollection())

    @property
    def renewed_date_time(self) -> datetime:
        """Gets the renewedDateTime property"""
        return self.properties.get("renewedDateTime", datetime.min)

    @property
    def resource_behavior_options(self) -> StringCollection:
        """Gets the resourceBehaviorOptions property"""
        return self.properties.get("resourceBehaviorOptions", StringCollection(None))

    @property
    def resource_provisioning_options(self) -> StringCollection:
        """Gets the resourceProvisioningOptions property"""
        return self.properties.get("resourceProvisioningOptions", StringCollection(None))

    @property
    def security_enabled(self) -> Optional[bool]:
        """Gets the securityEnabled property"""
        return self.properties.get("securityEnabled", None)

    @property
    def security_identifier(self) -> Optional[str]:
        """Gets the securityIdentifier property"""
        return self.properties.get("securityIdentifier", None)

    @property
    def service_provisioning_errors(self) -> ClientValueCollection[ServiceProvisioningError]:
        """Gets the serviceProvisioningErrors property"""
        return self.properties.get(
            "serviceProvisioningErrors", ClientValueCollection[ServiceProvisioningError](ServiceProvisioningError)
        )

    @property
    def theme(self) -> Optional[str]:
        """Gets the theme property"""
        return self.properties.get("theme", None)

    @property
    def unique_name(self) -> Optional[str]:
        """Gets the uniqueName property"""
        return self.properties.get("uniqueName", None)

    @property
    def visibility(self) -> Optional[str]:
        """Gets the visibility property"""
        return self.properties.get("visibility", None)

    @property
    def allow_external_senders(self) -> Optional[bool]:
        """Gets the allowExternalSenders property"""
        return self.properties.get("allowExternalSenders", None)

    @property
    def auto_subscribe_new_members(self) -> Optional[bool]:
        """Gets the autoSubscribeNewMembers property"""
        return self.properties.get("autoSubscribeNewMembers", None)

    @property
    def hide_from_address_lists(self) -> Optional[bool]:
        """Gets the hideFromAddressLists property"""
        return self.properties.get("hideFromAddressLists", None)

    @property
    def hide_from_outlook_clients(self) -> Optional[bool]:
        """Gets the hideFromOutlookClients property"""
        return self.properties.get("hideFromOutlookClients", None)

    @property
    def is_subscribed_by_mail(self) -> Optional[bool]:
        """Gets the isSubscribedByMail property"""
        return self.properties.get("isSubscribedByMail", None)

    @property
    def unseen_count(self) -> Optional[int]:
        """Gets the unseenCount property"""
        return self.properties.get("unseenCount", None)

    @property
    def welcome_message_enabled(self) -> Optional[bool]:
        """Gets the welcomeMessageEnabled property"""
        return self.properties.get("welcomeMessageEnabled", None)

    @property
    def is_archived(self) -> Optional[bool]:
        """Gets the isArchived property"""
        return self.properties.get("isArchived", None)

    @property
    def created_on_behalf_of(self) -> DirectoryObject:
        """Gets the createdOnBehalfOf property"""
        return self.properties.get(
            "createdOnBehalfOf", DirectoryObject(self.context, ResourcePath("createdOnBehalfOf", self.resource_path))
        )

    @property
    def member_of(self) -> EntityCollection[DirectoryObject]:
        """Gets the memberOf property"""
        return self.properties.get(
            "memberOf",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("memberOf", self.resource_path)
            ),
        )

    @property
    def members_with_license_errors(self) -> EntityCollection[DirectoryObject]:
        """Gets the membersWithLicenseErrors property"""
        return self.properties.get(
            "membersWithLicenseErrors",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("membersWithLicenseErrors", self.resource_path)
            ),
        )

    @property
    def on_premises_sync_behavior(self) -> OnPremisesSyncBehavior:
        """Gets the onPremisesSyncBehavior property"""
        return self.properties.get(
            "onPremisesSyncBehavior",
            OnPremisesSyncBehavior(self.context, ResourcePath("onPremisesSyncBehavior", self.resource_path)),
        )

    @property
    def settings(self) -> EntityCollection[GroupSetting]:
        """Gets the settings property"""
        return self.properties.get(
            "settings",
            EntityCollection[GroupSetting](self.context, GroupSetting, ResourcePath("settings", self.resource_path)),
        )

    @property
    def accepted_senders(self) -> EntityCollection[DirectoryObject]:
        """Gets the acceptedSenders property"""
        return self.properties.get(
            "acceptedSenders",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("acceptedSenders", self.resource_path)
            ),
        )

    @property
    def calendar(self) -> Calendar:
        """Gets the calendar property"""
        return self.properties.get("calendar", Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def calendar_view(self) -> EntityCollection[Event]:
        """Gets the calendarView property"""
        return self.properties.get(
            "calendarView",
            EntityCollection[Event](self.context, Event, ResourcePath("calendarView", self.resource_path)),
        )

    @property
    def drive(self) -> Drive:
        """Gets the drive property"""
        return self.properties.get("drive", Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def group_lifecycle_policies(self) -> EntityCollection[GroupLifecyclePolicy]:
        """Gets the groupLifecyclePolicies property"""
        return self.properties.get(
            "groupLifecyclePolicies",
            EntityCollection[GroupLifecyclePolicy](
                self.context, GroupLifecyclePolicy, ResourcePath("groupLifecyclePolicies", self.resource_path)
            ),
        )

    @property
    def photos(self) -> EntityCollection[ProfilePhoto]:
        """Gets the photos property"""
        return self.properties.get(
            "photos",
            EntityCollection[ProfilePhoto](self.context, ProfilePhoto, ResourcePath("photos", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Group"

    @property
    def on_premises_extension_attributes(self) -> OnPremisesExtensionAttributes:
        """Gets the onPremisesExtensionAttributes property"""
        from office365.directory.users.onpremisesextensionattributes import (
            OnPremisesExtensionAttributes,
        )

        return self.properties.get("onPremisesExtensionAttributes", OnPremisesExtensionAttributes())

    @property
    def organization_id(self) -> Optional[str]:
        """Gets the organizationId property"""
        return self.properties.get("organizationId", None)

    @property
    def access_type(self) -> GroupAccessType:
        """Gets the accessType property"""
        from office365.directory.groups.access_type import GroupAccessType

        return self.properties.get("accessType", GroupAccessType.none)

    @property
    def is_favorite(self) -> Optional[bool]:
        """Gets the isFavorite property"""
        return self.properties.get("isFavorite", None)

    @property
    def unseen_conversations_count(self) -> Optional[int]:
        """Gets the unseenConversationsCount property"""
        return self.properties.get("unseenConversationsCount", None)

    @property
    def unseen_messages_count(self) -> Optional[int]:
        """Gets the unseenMessagesCount property"""
        return self.properties.get("unseenMessagesCount", None)
