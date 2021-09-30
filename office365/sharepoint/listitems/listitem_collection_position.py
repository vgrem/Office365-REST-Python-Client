from office365.runtime.client_value import ClientValue


class ListItemCollectionPosition(ClientValue):

    def __init__(self, paging_info):
        super().__init__()
        self.PagingInfo = paging_info
