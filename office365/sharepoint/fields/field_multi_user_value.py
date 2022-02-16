from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.fields.field_user_value import FieldUserValue


class FieldMultiUserValue(FieldMultiLookupValue):

    def __init__(self):
        """Represents the multi valued user field for a list item."""
        super(FieldMultiUserValue, self).__init__()
        self._item_type = FieldUserValue
