from office365.runtime.clientValueCollection import ClientValueCollection
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue


class FieldMultiLookupValue(ClientValueCollection):

    def __init__(self):
        super().__init__(FieldLookupValue)
