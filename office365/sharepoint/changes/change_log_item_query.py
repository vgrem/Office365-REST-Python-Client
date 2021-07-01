from office365.runtime.client_value import ClientValue


class ChangeLogItemQuery(ClientValue):

    def __init__(self, change_token=None, contains=None, row_limit=None):
        """

        :type change_token: str
        :type contains: str
        :type row_limit: str
        """
        super(ChangeLogItemQuery, self).__init__()
        self.ChangeToken = change_token
        self.Contains = contains
        self.RowLimit = row_limit

    @property
    def entity_type_name(self):
        return 'SP.ChangeLogItemQuery'
