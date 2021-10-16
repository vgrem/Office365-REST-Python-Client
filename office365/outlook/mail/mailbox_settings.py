from office365.runtime.client_value import ClientValue


class MailboxSettings(ClientValue):
    """Settings for the primary mailbox of a user."""

    def __init__(self, time_format=None):
        super(MailboxSettings, self).__init__()
        self.timeFormat = time_format
