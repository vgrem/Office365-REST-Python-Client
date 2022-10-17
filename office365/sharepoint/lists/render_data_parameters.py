from office365.runtime.client_value import ClientValue


class RenderListDataParameters(ClientValue):
    """Specifies the parameters to be used to render list data as a JSON string"""

    def __init__(self, add_all_fields=None, add_required_fields=None):
        """
        :param bool add_all_fields:
        :param bool add_required_fields: This parameter indicates if we return required fields.
        """
        self.AddAllFields = add_all_fields
        self.AddRequiredFields = add_required_fields

    @property
    def entity_type_name(self):
        return "SP.RenderListDataParameters"
