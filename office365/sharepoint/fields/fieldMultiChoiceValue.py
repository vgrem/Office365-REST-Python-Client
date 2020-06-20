from office365.runtime.clientValueCollection import ClientValueCollection
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue


class FieldMultiChoiceValue(ClientValueCollection):

    def __init__(self, choices):
        super().__init__(str)
        [self.add(choice) for choice in choices]


