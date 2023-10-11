from office365.runtime.client_value import ClientValue


class UsageDetails(ClientValue):
    """Complex type containing properties of Used items. Information on when the resource was last accessed (viewed)
    or modified (edited) by the user."""

    def __init__(self, last_accessed_datetime=None, last_modified_datetime=None):
        """
        :param datetime.datetime last_accessed_datetime: The date and time the resource was last accessed by the user.
        :param datetime.datetime last_modified_datetime: The date and time the resource was last modified by the user.
        """
        self.lastAccessedDateTime = last_accessed_datetime
        self.lastModifiedDateTime = last_modified_datetime
