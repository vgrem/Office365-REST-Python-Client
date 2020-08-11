from office365.runtime.client_value import ClientValue


class SearchRequest(ClientValue):

    def __init__(self, query_text, selected_properties=None, refinement_filters=None,
                 blockDedupeMode=None, bypassResultTypes=None):
        """

        :type query_text: str
        :type selected_properties: dict
        :type refinement_filters: dict
        :type blockDedupeMode: int
        """
        super().__init__()
        self.Querytext = query_text
        self.BlockDedupeMode = blockDedupeMode
        self.BypassResultTypes = bypassResultTypes
        self.SelectProperties = selected_properties
        self.RefinementFilters = refinement_filters
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
