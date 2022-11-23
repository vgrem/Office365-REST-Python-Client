from office365.runtime.client_value import ClientValue


class ReportBase(ClientValue):

    def __init__(self):
        self.FarmId = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.ReportBase"
