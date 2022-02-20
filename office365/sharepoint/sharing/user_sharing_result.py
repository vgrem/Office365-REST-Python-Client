from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class UserSharingResult(ClientValue):
    """Specifies a sharing result for an individual user that method UpdateDocumentSharingInfo
    (section 3.2.5.187.2.1.1) returns."""

    def __init__(self):
        super(UserSharingResult, self).__init__()
        self.AllowedRoles = ClientValueCollection(int)
        self.CurrentRole = None
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
