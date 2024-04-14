from office365.runtime.client_value import ClientValue
from office365.sharepoint.directory.provider.alternate_id_data import AlternateIdData


class DirectoryObjectData(ClientValue):
    """"""

    def __init__(self, AlternateId=AlternateIdData(), Id=None):
        self.AlternateId = AlternateId
        self.Id = Id

    @property
    def entity_type_name(self):
        return "SP.Directory.Provider.DirectoryObjectData"
