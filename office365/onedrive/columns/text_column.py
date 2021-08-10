from office365.runtime.client_value import ClientValue


class TextColumn(ClientValue):
    """The textColumn on a columnDefinition resource indicates that the column's values are text."""

    def __init__(self, max_length=None):
        super(TextColumn, self).__init__()
        self.maxLength = max_length
