from office365.runtime.client_object import ClientObject


class SpoOperation(ClientObject):

    def __init__(self, context):
        super().__init__(context)

    @property
    def is_complete(self):
        if self.is_property_available("IsComplete"):
            return bool(self.properties["IsComplete"])
        return None

    @property
    def polling_interval_secs(self):
        if self.is_property_available("PollingInterval"):
            return int(self.properties["PollingInterval"]) / 1000
        return None
