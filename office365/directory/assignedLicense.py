from office365.runtime.client_value import ClientValue


class AssignedLicense(ClientValue):

    def __init__(self, skuId=None, disabledPlans=None):
        super().__init__()
        self.skuId = skuId
        self.disabledPlans = disabledPlans
