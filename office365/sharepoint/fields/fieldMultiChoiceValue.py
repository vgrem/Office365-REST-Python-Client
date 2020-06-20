from office365.runtime.clientValueCollection import ClientValueCollection
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue


class FieldMultiChoiceValue(ClientValueCollection):

    def __init__(self, choices):
        super().__init__()
        [self.add(c) for c in choices]

    def to_json(self):
        return {"results": self._data}

    @property
    def entity_type_name(self):
        return "Collection(Edm.String)"
