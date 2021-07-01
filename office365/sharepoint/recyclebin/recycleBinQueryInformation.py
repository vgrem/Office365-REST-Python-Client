from office365.runtime.client_value import ClientValue


class RecycleBinQueryInformation(ClientValue):

    def __init__(self, is_ascending, item_state, order_by, paging_info, row_limit, show_only_my_items):
        """

        :type show_only_my_items: bool
        :type row_limit: int
        :type paging_info: str
        :type order_by: int
        :type item_state: int
        :type is_ascending: bool
        """
        super(RecycleBinQueryInformation, self).__init__()
        self.IsAscending = is_ascending
        self.ItemState = item_state
        self.OrderBy = order_by
        self.PagingInfo = paging_info
        self.RowLimit = row_limit
        self.ShowOnlyMyItems = show_only_my_items
