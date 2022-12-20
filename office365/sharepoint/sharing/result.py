from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.groups.collection import GroupCollection
from office365.sharepoint.sharing.invitation.creation_result import SPInvitationCreationResult
from office365.sharepoint.sharing.user_sharing_result import UserSharingResult


class SharingResult(BaseEntity):
    """Contains properties generated as a result of sharing."""

    @property
    def url(self):
        """Gets the URL of the securable object being shared.

        :rtype: str or None
        """
        return self.properties.get("Url", None)

    @property
    def error_message(self):
        """Gets an error message about the failure if sharing was unsuccessful.

        :rtype: str or None
        """
        return self.properties.get("ErrorMessage", None)

    @property
    def name(self):
        """
        Gets the name of the securable object being shared.

        :rtype: str or None
        """
        return self.properties.get("Name", None)

    @property
    def icon_url(self):
        """
        Gets a URL to an icon that represents the securable object, if one exists.

        :rtype: str or None
        """
        return self.properties.get("IconUrl", None)

    @property
    def status_code(self):
        """
        Gets the enumeration value which summarizes the result of the sharing operation.

        :rtype: int or None
        """
        return self.properties.get("StatusCode", None)

    @property
    def permissions_page_relative_url(self):
        """
        Gets the relative URL of the page that shows permissions.

        :rtype: str or None
        """
        return self.properties.get("PermissionsPageRelativeUrl", None)

    @property
    def invited_users(self):
        """
        Gets a list of SPInvitationCreationResult (section 3.2.5.325) objects representing the external users being
        invited to have access.

        :rtype: ClientValueCollection
        """
        return self.properties.get("InvitedUsers", ClientValueCollection(SPInvitationCreationResult))

    @property
    def uniquely_permissioned_users(self):
        """

        :rtype: ClientValueCollection
        """
        return self.properties.get("UniquelyPermissionedUsers", ClientValueCollection(UserSharingResult))

    @property
    def groups_shared_with(self):
        """

        :rtype: ClientValueCollection
        """
        return self.properties.get("GroupsSharedWith",
                                   GroupCollection(self.context, ResourcePath("GroupsSharedWith", self.resource_path)))

    @property
    def users_added_to_group(self):
        """
        Gets the list of users being added to the SharePoint permissions group.

        :rtype: ClientValueCollection
        """
        return self.properties.get("UsersAddedToGroup", ClientValueCollection(UserSharingResult))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "GroupsSharedWith": self.groups_shared_with,
                "UsersAddedToGroup": self.users_added_to_group,
            }
            default_value = property_mapping.get(name, None)
        return super(SharingResult, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(SharingResult, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Name":
                pass
                # self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self
