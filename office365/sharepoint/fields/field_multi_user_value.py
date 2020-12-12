from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.fields.field_user_value import FieldUserValue


class FieldMultiUserValue(FieldMultiLookupValue):

    def __init__(self):
        super().__init__()
        self._item_type = FieldUserValue
