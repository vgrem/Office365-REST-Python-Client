from office365.runtime.client_value import ClientValue


class ShareLinkSettings(ClientValue):
    """Represents the settings the retrieval or creation/update of a tokenized sharing link"""

    def __init__(self, link_kind, expiration=None):
        """
        :param int link_kind: The kind of the tokenized sharing link to be created/updated or retrieved.
            This value MUST NOT be set to Uninitialized (section 3.2.5.315.1.1) nor Direct (section 3.2.5.315.1.2)
        """
        self.linkKind = link_kind
        self.expiration = expiration

    @property
    def entity_type_name(self):
        return "SP.Sharing.ShareLinkSettings"
