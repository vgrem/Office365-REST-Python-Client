from office365.entity import Entity
from office365.runtime.queries.service_operation import ServiceOperationQuery


class Subscription(Entity):
    """A subscription allows a client app to receive change notifications about changes to data in Microsoft Graph"""

    def reauthorize(self):
        """Reauthorize a subscription when you receive a reauthorizationRequired challenge."""
        qry = ServiceOperationQuery(self, "reauthorize")
        self.context.add_query(qry)
        return self

    @property
    def application_id(self):
        """
        Identifier of the application used to create the subscription.

        :rtype: str or None
        """
        return self.properties.get("applicationId", None)

    @property
    def resource(self):
        """
        Specifies the resource that will be monitored for changes.
        Do not include the base URL (https://graph.microsoft.com/v1.0/). See the possible resource path values for
        each supported resource.

        :rtype: str or None
        """
        return self.properties.get("resource", None)
