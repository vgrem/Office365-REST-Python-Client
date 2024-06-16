from office365.entity import Entity


class DataPolicyOperation(Entity):
    """
    Represents a submitted data policy operation. It contains necessary information for tracking the status of
    an operation. For example, a company administrator can submit a data policy operation request to export an
    employee's company data, and then later track that request.
    """
