from office365.runtime.client_value import ClientValue


class WorkbookFilterCriteria(ClientValue):
    """Represents the filtering criteria applied to a column."""

    def __init__(self, color=None, dynamicCriteria=None, operator=None, values=None):
        """
        :param str color:  The color applied to the cell.
        :param str dynamicCriteria:  A dynamic formula specified in a custom filter.
        :param str operator: An operator in a cell; for example, =, >, <, <=, or <>.
        :param list values: The values that appear in the cell.
        """
        self.color = color
        self.dynamicCriteria = dynamicCriteria
        self.operator = operator
        self.values = values
