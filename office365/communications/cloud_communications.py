from office365.communications.callrecords.call_record import CallRecord
from office365.communications.calls.call import Call
from office365.communications.onlinemeetings.collection import OnlineMeetingCollection
from office365.communications.presences.presence import Presence
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


class CloudCommunications(Entity):

    def get_presences_by_user_id(self, ids):
        """
        Get the presence information for multiple users.

        :type ids: list[str]
        """
        return_type = EntityCollection(self.context, Presence, ResourcePath("presences", self.resource_path))
        qry = ServiceOperationQuery(self, "getPresencesByUserId", None, {"ids": ids}, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def calls(self):
        """"
        :rtype: EntityCollection
        """
        return self.get_property('calls',
                                 EntityCollection(self.context, Call, ResourcePath("calls", self.resource_path)))

    @property
    def call_records(self):
        """"
        :rtype: EntityCollection
        """
        return self.get_property('callRecords',
                                 EntityCollection(self.context, CallRecord,
                                                  ResourcePath("callRecords", self.resource_path)))

    @property
    def online_meetings(self):
        """"
        :rtype: OnlineMeetingCollection
        """
        return self.get_property('onlineMeetings',
                                 OnlineMeetingCollection(self.context,
                                                         ResourcePath("onlineMeetings", self.resource_path)))

    @property
    def presences(self):
        """"
        :rtype: EntityCollection
        """
        return self.get_property('presences',
                                 EntityCollection(self.context, Presence,
                                                  ResourcePath("presences", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "callRecords": self.call_records,
                "onlineMeetings": self.online_meetings
            }
            default_value = property_mapping.get(name, None)
        return super(CloudCommunications, self).get_property(name, default_value)
