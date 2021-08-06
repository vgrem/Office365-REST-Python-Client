from office365.runtime.client_value import ClientValue


class AssignedLicense(ClientValue):
    """"""

    def __init__(self, sku_id=None, disabled_plans=None):
        super(AssignedLicense, self).__init__()
        self.skuId = sku_id
        self.disabledPlans = disabled_plans
