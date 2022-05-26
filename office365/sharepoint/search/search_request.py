from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.string_collection import StringCollection
from office365.sharepoint.search.query.sort import Sort


class SearchRequest(ClientValue):
    """
    The SearchRequest structure defines the HTTP BODY of the HTTP POST postquery operation as specified
    in section 3.1.5.7.2.1.3. The postquery operation together with the SearchRequest structure is similar
    to the query operation as specified in section 3.1.5.7.2.1.4, and is provided as a means to overcome
    Uniform Resource Locator (URL) length limitations that some clients experience with HTTP GET operations.
    """

    def __init__(self, query_text, select_properties=None, culture=None, trim_duplicates=False, **kwargs):
        """
        :param str query_text: Query expression
        :param list[str] or None select_properties:
        :param list[str] or None culture:
        :param bool or None trim_duplicates:
        """
        super(SearchRequest, self).__init__()
        self.Querytext = query_text
        self.SelectProperties = StringCollection(select_properties)
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = culture
        self.SortList = ClientValueCollection(Sort)
        self.TrimDuplicates = trim_duplicates
        self.__dict__.update(**kwargs)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
