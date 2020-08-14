from office365.runtime.client_value import ClientValue


class SearchRequest(ClientValue):

    def __init__(self, query_text, selected_properties=None, refinement_filters=None, refiners=None,
                 row_limit=None, rows_per_page=None, start_row=None, timeout=None,
                 block_dedupe_mode=None, bypass_result_types=None):
        """
        :type query_text: str
        :type selected_properties: dict
        :type refinement_filters: dict
        :type refiners: str
        :type row_limit: int
        :type rows_per_page: int
        :type start_row: int
        :type timeout: int
        :type bypassResultTypes: bool
        :type blockDedupeMode: int
        """
        super().__init__()
        self.Querytext = query_text
        self.SelectProperties = selected_properties
        self.RefinementFilters = refinement_filters
        self.Refiners = refiners

        self.RowLimit = row_limit
        self.RowsPerPage = rows_per_page
        self.StartRow = start_row

        self.Timeout = timeout

        self.BypassResultTypes = bypass_result_types
        self.BlockDedupeMode = block_dedupe_mode
        self.ClientType = None
        self.CollapseSpecification = None
        self.Culture = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchRequest"
