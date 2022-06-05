from office365.runtime.client_value import ClientValue


class Shared(ClientValue):

    def __init__(self, owner=None, shared_by=None):
        """
        The Shared resource indicates a DriveItem has been shared with others. The resource includes information
        about how the item is shared.

        :param office365.directory.identities.identity_set.IdentitySet owner: The identity of the owner of the shared
           item.
        :param office365.directory.identities.identity_set.IdentitySet shared_by: The identity of the user who shared
            the item
        """
        super(Shared, self).__init__()
        self.owner = owner
        self.sharedBy = shared_by
