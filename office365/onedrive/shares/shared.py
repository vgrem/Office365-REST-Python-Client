from office365.runtime.client_value import ClientValue


class Shared(ClientValue):

    def __init__(self, owner=None):
        """
        The Shared resource indicates a DriveItem has been shared with others. The resource includes information
        about how the item is shared.

        :type owner: office365.directory.identitySet.IdentitySet
        """
        super(Shared, self).__init__()
        self.owner = owner
