from office365.runtime.client_value import ClientValue


class SharingDetail(ClientValue):
    """Complex type containing properties of sharedInsight items."""

    def __init__(self, shared_datetime=None):
        """
        :param datetime.datetime shared_datetime: The date and time the file was last shared.
        """
        self.sharedDateTime = shared_datetime
