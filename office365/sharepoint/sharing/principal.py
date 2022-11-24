from office365.runtime.client_value import ClientValue


class Principal(ClientValue):
    """Principal class is a representation of an identity (user/group)."""

    @property
    def entity_type_name(self):
        return "SP.Sharing.Principal"
