from office365.communications.calls.participant import Participant
from office365.communications.operations.comms_operation import CommsOperation
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.resource_path import ResourcePath


class Call(Entity):
    """
    The call resource is created when there is an incoming call for the application or the application creates a
    new outgoing call via a POST on app/calls.
    """

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
