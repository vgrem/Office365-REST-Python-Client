from office365.runtime.client_value import ClientValue


class Principal(ClientValue):
    """Principal class is a representation of an identity (user/group)."""

    def __init__(self, directory_object_id=None, email=None, expiration=None):
        """
        :param str directory_object_id:
        :param str email: Email address of the Principal.
        :param str expiration:
        """
        self.directoryObjectId = directory_object_id
        self.email = email
        self.expiration = expiration

    @property
    def entity_type_name(self):
        return "SP.Sharing.Principal"
