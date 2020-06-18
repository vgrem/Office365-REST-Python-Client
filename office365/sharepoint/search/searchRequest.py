from office365.runtime.client_value_object import ClientValueObject


class SearchRequest(ClientValueObject):

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
