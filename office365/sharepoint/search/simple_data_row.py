from office365.runtime.client_value import ClientValue


class SimpleDataRow(ClientValue):

    def __init__(self, cells=None):
        if cells is None:
            cells = {}
        self.Cells = cells

    @staticmethod
    def _try_get_value(value):
        """
        :type value: dict
        """
        type_name = value.get('ValueType', None)
        raw_value = value.get("Value", None)
        try:
            if type_name == 'Edm.Int64':
                return int(raw_value)
            elif type_name == 'Edm.Double':
                return float(raw_value)
            elif type_name == 'Edm.Boolean':
                return raw_value == "true"
            else:
                return raw_value
        except ValueError:
            return raw_value

    def set_property(self, k, v, persist_changes=True):
        for k, v in v.items():
            key = v.get('Key', None)
            if key is not None:
                self.Cells[key] = self._try_get_value(v)

        return self
