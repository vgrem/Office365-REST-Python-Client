from office365.runtime.client_value import ClientValue
from office365.sharepoint.search.simple_data_table import SimpleDataTable


class RelevantResults(ClientValue):
    """
    The RelevantResults table contains the actual query results. It MUST only be present if the ResultTypes element
    in the properties element of the Execute message contains ResultType.RelevantResults,
    as specified in section 2.2.5.5
    """

    def __init__(self):
        super(RelevantResults, self).__init__()
        self.GroupTemplateId = None
        self.ItemTemplateId = None
        self.Properties = []
        self.ResultTitle = None
        self.ResultTitleUrl = None
        self.RowCount = None
        self.Table = SimpleDataTable()
        self.TotalRows = None
        self.TotalRowsIncludingDuplicates = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.RelevantResults"
