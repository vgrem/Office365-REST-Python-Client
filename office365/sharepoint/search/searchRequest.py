from office365.runtime.clientValue import ClientValue


class SearchRequest(ClientValue):

    def __init__(self, query_text, blockDedupeMode=None, bypassResultTypes=None):
        """

        :type bypassResultTypes: bool
        :type blockDedupeMode: int
        :type query_text: str
        """
        super().__init__()
        self.Querytext = query_text
        self.BlockDedupeMode = blockDedupeMode
        self.BypassResultTypes = bypassResultTypes
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
