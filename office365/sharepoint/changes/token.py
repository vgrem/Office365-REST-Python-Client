from office365.runtime.client_value import ClientValue


class ChangeToken(ClientValue):
    """Represents the unique sequential location of a change within the change log. Client applications can use the
    change token as a starting point for retrieving changes."""

    def __init__(self, string_value=None):
        super(ChangeToken, self).__init__()
        self.StringValue = string_value

    def __repr__(self):
        return self.StringValue or ""
