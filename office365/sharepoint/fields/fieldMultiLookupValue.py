from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.fields.field_lookup_value import FieldLookupValue


class FieldMultiLookupValue(ClientValueCollection):

    def __init__(self):
        super().__init__(FieldLookupValue)
