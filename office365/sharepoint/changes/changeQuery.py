from office365.runtime.clientValue import ClientValue


class ChangeQuery(ClientValue):
    """Defines a query that is performed against the change log."""

    @property
    def entity_type_name(self):
        return 'SP.ChangeQuery'
