from office365.runtime.client_value import ClientValue


class WorkbookFilterCriteria(ClientValue):
    """Represents the filtering criteria applied to a column."""

    def __init__(self, operator=None, values=None):
        """ """
        self.operator = operator
        self.values = values
