from office365.runtime.client_value import ClientValue


class SimpleDataRow(ClientValue):

    def __init__(self, cells=None):
        if cells is None:
            cells = {}
        self.Cells = cells

    def set_property(self, k, v, persist_changes=True):
        for k, v in v.items():
            key = v.get('Key', None)
            type_name = v.get('ValueType', None)
            if key is not None:
                self.Cells[key] = v.get("Value", None)
        return self
