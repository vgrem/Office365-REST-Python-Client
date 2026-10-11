from office365.runtime.client_value import ClientValue


class HuntingRowResult(ClientValue):
    """Represents a row of the results from running an advanced hunting query.

    The content of the results is depended on the submitted KQL query, see KQL quick reference.
    """
