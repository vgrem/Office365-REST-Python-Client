from office365.runtime.client_value import ClientValue


class SearchRequest(ClientValue):

    def __init__(self, query_text, **kwargs):
        super(SearchRequest, self).__init__()
        self.Querytext = query_text
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = None
        self.__dict__.update(**kwargs)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
