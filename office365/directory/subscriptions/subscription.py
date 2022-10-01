from office365.entity import Entity


class Subscription(Entity):
    """A subscription allows a client app to receive change notifications about changes to data in Microsoft Graph"""

    @property
    def application_id(self):
        """
        Identifier of the application used to create the subscription.

        :rtype: str or None
        """
        return self.properties.get("applicationId", None)
