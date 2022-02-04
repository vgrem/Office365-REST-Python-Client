from office365.runtime.client_value import ClientValue


class SPInvitationCreationResult(ClientValue):

    def __init__(self):
        super(SPInvitationCreationResult, self).__init__()
        self.Email = None
        self.InvitationLink = None
        self.Succeeded = None
