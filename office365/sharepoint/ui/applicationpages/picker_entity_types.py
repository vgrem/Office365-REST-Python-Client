from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue


class PickerEntityInformation(ClientObject):
    pass


class PickerEntityInformationRequest(ClientValue):

    def __init__(self, EmailAddress=None, GroupId=None, Key=None, PrincipalType=None):
        super().__init__()
        self.EmailAddress = EmailAddress
        self.GroupId = GroupId
        self.Key = Key
        self.PrincipalType = PrincipalType

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.PickerEntityInformationRequest"
