from office365.runtime.clientValueCollection import ClientValueCollection
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue


class FieldMultiLookupValue(ClientValueCollection):

    def __init__(self):
        super().__init__()

    @staticmethod
    def from_lookup(ids):
        val = FieldMultiLookupValue()
        [val.add(FieldLookupValue(lookup_id)) for lookup_id in ids]
        return val

    def to_json(self):
        lookup_ids = [v.LookupId for v in self]
        return {"results": lookup_ids}

    @property
    def entity_type_name(self):
        return "Collection(Edm.Int32)"
