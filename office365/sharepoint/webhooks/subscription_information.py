from office365.runtime.client_value import ClientValue


class SubscriptionInformation(ClientValue):

    def __init__(self, notificationUrl=None, resource=None):
        super().__init__()
        self.notificationUrl = notificationUrl
        self.resource = resource
