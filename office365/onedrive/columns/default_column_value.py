from office365.runtime.client_value import ClientValue


class DefaultColumnValue(ClientValue):
    """The defaultColumnValue on a columnDefinition resource specifies the default value for this column.
    The default value can either be specified directly or as a formula."""

    def __init__(self, formula=None, value=None):
        super(DefaultColumnValue, self).__init__()
        self.formula = formula
        self.value = value
