from office365.runtime.client_value import ClientValue


class SubscriptionInformation(ClientValue):

    def __init__(self, notification_url=None, resource=None):
        super(SubscriptionInformation, self).__init__()
        self.notificationUrl = notification_url
        self.resource = resource
