from office365.runtime.client_value import ClientValue


class ProvisionedPlan(ClientValue):
    """
    The provisionedPlans property of the user entity and the organization entity is a collection of provisionedPlan.
    """

    def __init__(self, service=None):
        """
        :param str service:
        """
        self.service = service

    def __repr__(self):
        return self.service


