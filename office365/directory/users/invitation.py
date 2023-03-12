from office365.directory.users.invited_user_message_info import InvitedUserMessageInfo
from office365.directory.users.user import User
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery


class Invitation(Entity):
    """Represents an invitation that is used to add external users to an organization."""

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


class InvitationCollection(EntityCollection):
    """Invitation's collection"""

    def __init__(self, context, resource_path=None):
        super(InvitationCollection, self).__init__(context, Invitation, resource_path)

    def create(self, invited_user_email_address, invite_redirect_url=None):
        """
        Use this API to create a new invitation. Invitation adds an external user to the organization.

        When creating a new invitation you have several options available:

          - On invitation creation, Microsoft Graph can automatically send an invitation email directly to
          the invited user, or your app can use the inviteRedeemUrl returned in the creation response to craft your
          own invitation (through your communication mechanism of choice) to the invited user.
          If you decide to have Microsoft Graph send an invitation email automatically, you can control the content
          and language of the email using invitedUserMessageInfo.
          - When the user is invited, a user entity (of userType Guest) is created and can now be used to control
          access to resources. The invited user has to go through the redemption process to access any resources
          they have been invited to.

          :param str invited_user_email_address: The email address of the user you are inviting.
          :param str invite_redirect_url: The URL that the user will be redirected to after redemption.
        """
        return_type = Invitation(self.context)
        properties = {"invitedUserEmailAddress": invited_user_email_address,
                      "inviteRedirectUrl": invite_redirect_url}
        qry = CreateEntityQuery(self, properties, return_type)
        self.context.add_query(qry)
        self.add_child(return_type)
        return return_type

