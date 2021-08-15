from office365.runtime.client_value import ClientValue


class SharingLink(ClientValue):
    """The SharingLink resource groups link-related data items into a single structure."""

    def __init__(self, _type=None, scope=None):
        """
        :param str _type: The type of the link created.
        :param str scope: The scope of the link represented by this permission. Value anonymous indicates the link is
             usable by anyone, organization indicates the link is only usable for users signed into the same tenant.
        """
        super(SharingLink, self).__init__()
        self.type = _type
        self.scope = scope
