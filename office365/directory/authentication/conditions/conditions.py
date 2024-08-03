from office365.directory.authentication.conditions.applications import (
    AuthenticationConditionsApplications,
)
from office365.runtime.client_value import ClientValue


class AuthenticationConditions(ClientValue):
    """"""

    def __init__(self, applications=AuthenticationConditionsApplications()):
        self.applications = applications
