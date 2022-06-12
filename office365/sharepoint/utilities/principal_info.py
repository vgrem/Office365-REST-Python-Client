from office365.runtime.client_value import ClientValue


class PrincipalInfo(ClientValue):
    """Provides access to information about a principal."""

    @property
    def entity_type_name(self):
        return "SP.Utilities.PrincipalInfo"
