from office365.runtime.client_value import ClientValue


class AssignedPlan(ClientValue):
    """
    The assignedPlans property of both the user entity and the organization entity is a collection of assignedPlan.
    """

    def __init__(self, assigned_datetime=None):
        """
        :param datetime assigned_datetime: The date and time at which the plan was assigned.
        """
        self.assignedDateTime = assigned_datetime

