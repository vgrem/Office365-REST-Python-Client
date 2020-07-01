from office365.runtime.clientValue import ClientValue


class SPInvitationCreationResult(ClientValue):

    def __init__(self):
        super().__init__("SP")
        self.Email = None
        self.InvitationLink = None
        self.Succeeded = None
