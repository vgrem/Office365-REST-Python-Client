from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class UserSharingResult(ClientValue):
    """Specifies a sharing result for an individual user that method UpdateDocumentSharingInfo
    (section 3.2.5.187.2.1.1) returns."""

    def __init__(
        self,
        allowed_roles=None,
        current_role=None,
        display_name=None,
        email=None,
        invitation_link=None,
        is_user_known=None,
        message=None,
        status=None,
        user=None,
    ):
        """
        :param list[int] allowed_roles: Specifies a set of roles that can be assigned to the user.
        :param int current_role: Specifies the role that the user is currently assigned to.
        :param str display_name: Gets the display name of the user.
        :param str email: Gets the user email.
        :param str invitation_link: Gets the invitation link.
        :param bool is_user_known: Specifies whether the user is known to the server. If "true", the user is known to
            the server; if "false", user is unknown.
        :param str message: Specifies a message string that explains the reason when the Status  property is "false".
        :param bool status: Specifies whether the sharing update for the user was completed successfully. If "true",
            the sharing update completed successfully for the user; if "false", the sharing update failed for the user.
        :param str user: Specifies the identifier of a user.
        """
        super(UserSharingResult, self).__init__()
        self.AllowedRoles = ClientValueCollection(int, allowed_roles)
        self.CurrentRole = current_role
        self.DisplayName = display_name
        self.Email = email
        self.InvitationLink = invitation_link
        self.IsUserKnown = is_user_known
        self.Message = message
        self.Status = status
        self.User = user

    @property
    def entity_type_name(self):
        return "SP.Sharing"
