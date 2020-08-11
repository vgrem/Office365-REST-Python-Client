from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class UserSharingResult(ClientValue):

    def __init__(self):
        super().__init__("SP.Sharing")
        self.AllowedRoles = ClientValueCollection(int)
        self.CurrentRole = None
        self.DisplayName = None
        self.Email = None
        self.InvitationLink = None
        self.IsUserKnown = None
        self.Message = None
        self.Status = None
        self.User = None
