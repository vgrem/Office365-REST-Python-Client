from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.group_collection import GroupCollection
from office365.sharepoint.sharing.invitation_creation_result import SPInvitationCreationResult
from office365.sharepoint.sharing.user_sharing_result import UserSharingResult


class SharingResult(BaseEntity):

    @property
    def error_message(self):
        return self.properties.get("ErrorMessage", None)

    @property
    def name(self):
        return self.properties.get("Name", None)

    @property
    def icon_url(self):
        return self.properties.get("IconUrl", None)

    @property
    def statusCode(self):
        return self.properties.get("StatusCode", None)

    @property
    def permissions_page_relative_url(self):
        return self.properties.get("PermissionsPageRelativeUrl", None)

    @property
    def invited_users(self):
        return self.properties.get("InvitedUsers", ClientValueCollection(SPInvitationCreationResult))

    @property
    def uniquely_permissioned_users(self):
        return self.properties.get("UniquelyPermissionedUsers", ClientValueCollection(UserSharingResult))

    @property
    def groups_shared_with(self):
        return self.properties.get("GroupsSharedWith",
                                   GroupCollection(self.context, ResourcePath("GroupsSharedWith", self.resource_path)))
