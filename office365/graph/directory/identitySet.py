from office365.graph.directory.identity import Identity
from office365.runtime.client_value_object import ClientValueObject


class IdentitySet(ClientValueObject):
    """The IdentitySet resource is a keyed collection of identity resources. It is used to represent a set of
    identities associated with various events for an item, such as created by or last modified by. """

    def __init__(self):
        super(IdentitySet, self).__init__()
        self.application = Identity()
        self.device = Identity()
        self.user = Identity()
