from office365.runtime.client_value import ClientValue


class ChangeQuery(ClientValue):
    """Defines a query that is performed against the change log."""

    @property
    def entity_type_name(self):
        return 'SP.ChangeQuery'
