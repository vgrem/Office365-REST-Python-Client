from office365.runtime.client_value_object import ClientValueObject


class Identity(ClientValueObject):
    """The Identity resource represents an identity of an actor. For example, an actor can be a user, device,
    or application. """

    def __init__(self):
        super(Identity, self).__init__()
        self.displayName = None
        self.id = None
