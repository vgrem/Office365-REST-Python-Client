from office365.runtime.clientValue import ClientValue
from office365.sharepoint.search.simpleDataTable import SimpleDataTable


class RelevantResults(ClientValue):

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
