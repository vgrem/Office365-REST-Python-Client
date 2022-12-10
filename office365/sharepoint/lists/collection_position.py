from office365.runtime.client_value import ClientValue


class ListCollectionPosition(ClientValue):

    def __init__(self, paging_info=None):
        """
        :param str paging_info:
        """
        self.PagingInfo = paging_info

    @property
    def entity_type_name(self):
        return "SP.ListCollectionPosition"
