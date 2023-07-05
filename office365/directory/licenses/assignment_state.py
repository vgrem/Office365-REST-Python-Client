from office365.runtime.client_value import ClientValue


class LicenseAssignmentState(ClientValue):
    """
    The licenseAssignmentStates property of the user entity is a collection of licenseAssignmentState objects.
    It provides details about license assignments to a user. The details include information such as:

        - What plans are disabled for a user
        - Whether the license was assigned to the user directly or inherited from a group
        - The current state of the assignment
        - Error details if the assignment state is Error
    """
    def __init__(self, assigned_by_group=None):
        """
        :param str assigned_by_group:
        """
        self.assignedByGroup = assigned_by_group
