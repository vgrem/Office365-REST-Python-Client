from __future__ import annotations

from typing import TYPE_CHECKING, List

from office365.communications.callrecords.collection import CallRecordCollection
from office365.communications.calls.collection import CallCollection
from office365.communications.onlinemeetings.collection import OnlineMeetingCollection
from office365.communications.presences.presence import Presence
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.communications.adhoc_call import AdhocCall
    from office365.communications.onlinemeetings.engagement_conversation import (
        OnlineMeetingEngagementConversation,
    )


class CloudCommunications(Entity):
    """ """

    def get_presences_by_user_id(self, ids: List[str]) -> EntityCollection[Presence]:
        """Get the presence information for multiple users.

        Args:
            ids (list[str]): The user object IDs.
        """
        return_type = EntityCollection(self.context, Presence, ResourcePath("presences", self.resource_path))
        qry = ServiceOperationQuery(self, "getPresencesByUserId", None, {"ids": ids}, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def calls(self) -> CallCollection:
        """ " """
        return self.properties.get("calls", CallCollection(self.context, ResourcePath("calls", self.resource_path)))

    @odata(name="callRecords")
    @property
    def call_records(self) -> CallRecordCollection:
        """ " """
        return self.properties.get(
            "callRecords", CallRecordCollection(self.context, ResourcePath("callRecords", self.resource_path))
        )

    @odata(name="onlineMeetings")
    @property
    def online_meetings(self) -> OnlineMeetingCollection:
        """ " """
        return self.properties.get(
            "onlineMeetings", OnlineMeetingCollection(self.context, ResourcePath("onlineMeetings", self.resource_path))
        )

    @property
    def presences(self) -> EntityCollection[Presence]:
        """ " """
        return self.properties.get(
            "presences", EntityCollection(self.context, Presence, ResourcePath("presences", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudCommunications"

    @property
    def adhoc_calls(self) -> EntityCollection[AdhocCall]:
        """Gets the adhocCalls property"""
        from office365.communications.adhoc_call import AdhocCall

        return self.properties.get(
            "adhocCalls",
            EntityCollection[AdhocCall](self.context, AdhocCall, ResourcePath("adhocCalls", self.resource_path)),
        )

    @property
    def online_meeting_conversations(self) -> EntityCollection[OnlineMeetingEngagementConversation]:
        """Gets the onlineMeetingConversations property"""
        from office365.communications.onlinemeetings.engagement_conversation import (
            OnlineMeetingEngagementConversation,
        )

        return self.properties.get(
            "onlineMeetingConversations",
            EntityCollection[OnlineMeetingEngagementConversation](
                self.context,
                OnlineMeetingEngagementConversation,
                ResourcePath("onlineMeetingConversations", self.resource_path),
            ),
        )
