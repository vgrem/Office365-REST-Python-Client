from office365.runtime.client_value import ClientValue


class ServicePlanInfo(ClientValue):
    """Contains information about a service plan associated with a subscribed SKU. The servicePlans property of
    the subscribedSku entity is a collection of servicePlanInfo."""

    def __init__(self, servicePlanId=None, servicePlanName=None, provisioningStatus=None, appliesTo=None):
        """

        :param str appliesTo: The object the service plan can be assigned to. Possible values:
               "User" - service plan can be assigned to individual users.
               "Company" - service plan can be assigned to the entire tenant.
        :param str provisioningStatus: The provisioning status of the service plan. Possible values:
               "Success" - Service is fully provisioned.
               "Disabled" - Service has been disabled.
               "PendingInput" - Service is not yet provisioned; awaiting service confirmation.
               "PendingActivation" - Service is provisioned but requires explicit activation by administrator
               (for example, Intune_O365 service plan)
               "PendingProvisioning" - Microsoft has added a new service to the product SKU and it has not been
               activated in the tenant, yet.
        :param str servicePlanName: The name of the service plan.
        :param str servicePlanId: The unique identifier of the service plan.
        """
        super().__init__()
        self.servicePlanId = servicePlanId
        self.servicePlanName = servicePlanName
        self.provisioningStatus = provisioningStatus
        self.appliesTo = appliesTo
