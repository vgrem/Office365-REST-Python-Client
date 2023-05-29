from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


class RemoteItem(ClientValue):
    """
    The remoteItem resource indicates that a driveItem references an item that exists in another drive.
    This resource provides the unique IDs of the source drive and target item.

    DriveItems with a non-null remoteItem facet are resources that are shared, added to the user's OneDrive,
    or on items returned from hetrogenous collections of items (like search results).
    """

    def __init__(self, created_by=IdentitySet(), created_datetime=None):
        """
        :param IdentitySet created_by:
        :param datetime.datetime created_datetime:
        """
        self.createdBy = created_by
        self.createdDateTime = created_datetime
