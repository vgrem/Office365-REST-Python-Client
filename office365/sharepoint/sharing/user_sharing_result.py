from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class UserSharingResult(ClientValue):
    """Specifies a sharing result for an individual user that method UpdateDocumentSharingInfo
    (section 3.2.5.187.2.1.1) returns."""

    def __init__(self, allowed_roles=None, current_role=None):
        """
        :param list[int] allowed_roles: Specifies a set of roles that can be assigned to the user.
        :param int current_role: Specifies the role that the user is currently assigned to.
        """
        super(UserSharingResult, self).__init__()
        self.AllowedRoles = ClientValueCollection(int, allowed_roles)
        self.CurrentRole = current_role
        self.DisplayName = None
        self.Email = None
        self.InvitationLink = None
        self.IsUserKnown = None
        self.Message = None
        self.Status = None
        self.User = None

    @property
    def entity_type_name(self):
        return "SP.Sharing"
