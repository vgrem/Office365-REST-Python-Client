from office365.runtime.clientValueCollection import ClientValueCollection
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.group_collection import GroupCollection
from office365.sharepoint.sharing.invitationCreationResult import SPInvitationCreationResult
from office365.sharepoint.sharing.userSharingResult import UserSharingResult


class SharingResult(BaseEntity):

    def __init__(self, context):
        super().__init__(context)

    @property
    def errorMessage(self):
        return self.properties.get("ErrorMessage", None)

    @property
    def name(self):
        return self.properties.get("Name", None)

    @property
    def iconUrl(self):
        return self.properties.get("IconUrl", None)

    @property
    def statusCode(self):
        return self.properties.get("StatusCode", None)

    @property
    def permissionsPageRelativeUrl(self):
        return self.properties.get("PermissionsPageRelativeUrl", None)

    @property
    def invited_users(self):
        return self.properties.get("InvitedUsers", ClientValueCollection(SPInvitationCreationResult()))

    @property
    def uniquelyPermissionedUsers(self):
        return self.properties.get("UniquelyPermissionedUsers", ClientValueCollection(UserSharingResult()))

    @property
    def groupsSharedWith(self):
        return self.properties.get("GroupsSharedWith",
                                   GroupCollection(self.context, ResourcePath("GroupsSharedWith", self.resource_path)))

