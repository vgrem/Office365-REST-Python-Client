from office365.communications.calls.call_route import CallRoute
from office365.communications.calls.participant import Participant
from office365.communications.operations.comms import CommsOperation
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath


class Call(Entity):
    """
    The call resource is created when there is an incoming call for the application or the application creates a
    new outgoing call via a POST on app/calls.
    """

    @property
    def callback_uri(self):
        """The callback URL on which callbacks will be delivered. Must be https."""
        return self.properties.get("callbackUri", None)

    @property
    def call_routes(self):
        """The routing information on how the call was retargeted. Read-only."""
        return self.properties.get("callRoutes", ClientValueCollection(CallRoute))

    @property
    def participants(self):
        """
        :rtype: EntityCollection
        """
        return self.get_property('participants',
                                 EntityCollection(self.context, Participant,
                                                  ResourcePath("participants", self.resource_path)))

    @property
    def operations(self):
        """
        :rtype: EntityCollection
        """
        return self.get_property('operations',
                                 EntityCollection(self.context, CommsOperation,
                                                  ResourcePath("operations", self.resource_path)))
