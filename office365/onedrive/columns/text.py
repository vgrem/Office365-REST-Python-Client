from office365.runtime.client_value import ClientValue


class TextColumn(ClientValue):
    """The textColumn on a columnDefinition resource indicates that the column's values are text."""

    def __init__(self, max_length=None, allow_multiple_lines=None):
        """
        :param int max_length: The maximum number of characters for the value.
        :param bool allow_multiple_lines: Whether to allow multiple lines of text.
        """
        super(TextColumn, self).__init__()
        self.maxLength = max_length
        self.allowMultipleLines = allow_multiple_lines
