from office365.directory.invitations.message_info import InvitedUserMessageInfo
from office365.directory.users.user import User
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class Invitation(Entity):
    """Represents an invitation that is used to add external users to an organization."""

    @property
    def invited_user_display_name(self):
        """The display name of the user being invited.
        :rtype: str
        """
        return self.properties.get("invitedUserDisplayName", None)

    @property
    def invited_user_email_address(self):
        """The email address of the user being invited.
        :rtype: str
        """
        return self.properties.get("invitedUserEmailAddress", None)

    @property
    def invited_user_message_info(self):
        return self.properties.get("invitedUserMessageInfo", InvitedUserMessageInfo())

    @property
    def invited_user(self):
        """The user created as part of the invitation creation."""
        return self.properties.get('invitedUser',
                                   User(self.context, ResourcePath("invitedUser", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "invitedUserMessageInfo": self.invited_user_message_info,
                "invitedUser": self.invited_user
            }
            default_value = property_mapping.get(name, None)
        return super(Invitation, self).get_property(name, default_value)


