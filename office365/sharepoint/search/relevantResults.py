from office365.runtime.client_value_object import ClientValueObject
from office365.sharepoint.simpleDataTable import SimpleDataTable


class RelevantResults(ClientValueObject):

    def __init__(self):
        super().__init__()
        self.GroupTemplateId = None
        self.ItemTemplateId = None
        self.Properties = []
        self.ResultTitle = None
        self.ResultTitleUrl = None
        self.RowCount = None
        self.Table = SimpleDataTable()
        self.TotalRows = None
        self.TotalRowsIncludingDuplicates = None
