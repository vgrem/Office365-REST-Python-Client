from office365.runtime.clientValue import ClientValue


class PickerEntityInformationRequest(ClientValue):

    def __init__(self):
        super().__init__()
        self.Key = None
        self.GroupId = None
        self.PrincipalType = None
        self.EmailAddress = None
