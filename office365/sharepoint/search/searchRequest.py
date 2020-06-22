from office365.runtime.clientValue import ClientValue


class SearchRequest(ClientValue):

    def __init__(self, query_text):
        super().__init__()
        self.Querytext = query_text
        self.BlockDedupeMode = None
        self.BypassResultTypes = None
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
