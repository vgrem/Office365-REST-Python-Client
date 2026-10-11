from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.communications.callrecords.modality import Modality
from office365.communications.calls.direction import CallDirection
from office365.communications.calls.incoming_context import IncomingContext
from office365.communications.calls.invitation_participant_info import (
    InvitationParticipantInfo,
)
from office365.communications.calls.options import CallOptions
from office365.communications.calls.participant import Participant
from office365.communications.calls.participant_info import ParticipantInfo
from office365.communications.calls.route import CallRoute
from office365.communications.calls.state import CallState
from office365.communications.meetings.info import MeetingInfo
from office365.communications.onlinemeetings.collection import ChatInfo
from office365.communications.operations.cancel_media_processing import (
    CancelMediaProcessingOperation,
)
from office365.communications.operations.comms import CommsOperation
from office365.communications.operations.unmute_participant import (
    UnmuteParticipantOperation,
)
from office365.communications.operations.update_recording_status import (
    UpdateRecordingStatusOperation,
)
from office365.communications.quotas import CALL_QUOTAS
from office365.communications.result_info import ResultInfo
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.limits import limit
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.communications.calls.audio_routing_group import AudioRoutingGroup
    from office365.communications.calls.content_sharing_session import (
        ContentSharingSession,
    )
    from office365.communications.calls.media_state import CallMediaState
    from office365.communications.calls.transcription_info import CallTranscriptionInfo
    from office365.communications.media_config import MediaConfig
    from office365.communications.tone_info import ToneInfo


@limit(*CALL_QUOTAS)
class Call(Entity):
    """
    The call resource is created when there is an incoming call for the application or the application creates a
    new outgoing call via a POST on app/calls.
    """

    def cancel_media_processing(self, client_context=None):
        """Cancels processing for any in-progress media operations.

        Media operations refer to the IVR operations playPrompt and recordResponse, which are by default queued
        to process in order. The cancelMediaProcessing method cancels any operation that is in-process as well as
        operations that are queued. For example, this method can be used to clean up the IVR operation queue for
        a new media operation. However, it will not cancel a subscribeToTone operation because it operates independent
        of any operation queue.

        Args:
            client_context (str): The client context.
        """
        return_type = CancelMediaProcessingOperation(self.context)
        payload = {"clientContext": client_context}
        qry = ServiceOperationQuery(self, "cancelMediaProcessing", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def reject(self, reason=None, callback_uri=None):
        """Enable a bot to reject an incoming call. The incoming call request can be an invite from a participant in
        a group call or a peer-to-peer call. If an invite to a group call is received, the notification will contain
        the chatInfo and meetingInfo parameters.

        The bot is expected to answer or reject the call before the call times out. The current timeout value is
        15 seconds.

        This API does not end existing calls that have already been answered. Use delete call to end a call.

        Args:
            reason (str): The rejection reason. Possible values are None, Busy and Forbidden
            callback_uri (str): This allows bots to provide a specific callback URI for the current call to receive
            later notifications. If this property has not been set, the bot's global callback URI will be used instead.
             This must be https.
        """
        payload = {"reason": reason, "callbackUri": callback_uri}
        qry = ServiceOperationQuery(self, "reject", None, payload)
        self.context.add_query(qry)
        return self

    def delete(self):
        """
        Delete or hang up an active call. For group calls, this will only delete your call leg and the underlying
        group call will still continue."""
        return super().delete_object()

    def update_recording_status(self, status, client_context):
        """Update the application's recording status associated with a call.
        This requires the use of the Teams policy-based recording solution.

        Args:
            status (str): The recording status. Possible values are: notRecording, recording, or failed.
            client_context (str): Unique client context string. Max limit is 256 chars.
        """
        return_type = UpdateRecordingStatusOperation(self.context)
        payload = {"status": status, "clientContext": client_context}
        qry = ServiceOperationQuery(self, "updateRecordingStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unmute(self, client_context):
        """Allow the application to unmute itself.

        This is a server unmute, meaning that the server will start sending audio packets for this participant
        to other participants again.

        Args:
            client_context (str): Unique Client Context string. Max limit is 256 chars.
        """
        return_type = UnmuteParticipantOperation(self.context)
        payload = {"clientContext": client_context}
        qry = ServiceOperationQuery(self, "unmute", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def callback_uri(self):
        """The callback URL on which callbacks will be delivered. Must be https."""
        return self.properties.get("callbackUri", None)

    @property
    def call_routes(self):
        """The routing information on how the call was retargeted. Read-only."""
        return self.properties.get("callRoutes", ClientValueCollection(CallRoute))

    @property
    def incoming_context(self):
        """Call context associated with an incoming call."""
        return self.properties.get("incomingContext", IncomingContext())

    @property
    def participants(self):
        """
        Participant collection
        """
        return self.properties.get(
            "participants", EntityCollection(self.context, Participant, ResourcePath("participants", self.resource_path))
        )

    @property
    def operations(self):
        """
        CommsOperation collection
        """
        return self.properties.get(
            "operations", EntityCollection(self.context, CommsOperation, ResourcePath("operations", self.resource_path))
        )

    @property
    def call_chain_id(self) -> Optional[str]:
        """Gets the callChainId property"""
        return self.properties.get("callChainId", None)

    @property
    def call_options(self) -> CallOptions:
        """Gets the callOptions property"""
        return self.properties.get("callOptions", CallOptions())

    @property
    def chat_info(self) -> ChatInfo:
        """Gets the chatInfo property"""
        return self.properties.get("chatInfo", ChatInfo())

    @property
    def direction(self) -> CallDirection:
        """Gets the direction property"""
        return self.properties.get("direction", CallDirection.incoming)

    @property
    def meeting_info(self) -> MeetingInfo:
        """Gets the meetingInfo property"""
        return self.properties.get("meetingInfo", MeetingInfo())

    @property
    def my_participant_id(self) -> Optional[str]:
        """Gets the myParticipantId property"""
        return self.properties.get("myParticipantId", None)

    @property
    def requested_modalities(self) -> ClientValueCollection[Modality]:
        """Gets the requestedModalities property"""
        return self.properties.get("requestedModalities", ClientValueCollection[Modality](Modality))

    @property
    def result_info(self) -> ResultInfo:
        """Gets the resultInfo property"""
        return self.properties.get("resultInfo", ResultInfo())

    @property
    def source(self) -> ParticipantInfo:
        """Gets the source property"""
        return self.properties.get("source", ParticipantInfo())

    @property
    def state(self) -> CallState:
        """Gets the state property"""
        return self.properties.get("state", CallState.incoming)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def targets(self) -> ClientValueCollection[InvitationParticipantInfo]:
        """Gets the targets property"""
        return self.properties.get(
            "targets", ClientValueCollection[InvitationParticipantInfo](InvitationParticipantInfo)
        )

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Call"

    @property
    def media_config(self) -> MediaConfig:
        """Gets the mediaConfig property"""
        from office365.communications.media_config import MediaConfig

        return self.properties.get("mediaConfig", MediaConfig())

    @property
    def media_state(self) -> CallMediaState:
        """Gets the mediaState property"""
        from office365.communications.calls.media_state import CallMediaState

        return self.properties.get("mediaState", CallMediaState())

    @property
    def tone_info(self) -> ToneInfo:
        """Gets the toneInfo property"""
        from office365.communications.tone_info import ToneInfo

        return self.properties.get("toneInfo", ToneInfo())

    @property
    def transcription(self) -> CallTranscriptionInfo:
        """Gets the transcription property"""
        from office365.communications.calls.transcription_info import (
            CallTranscriptionInfo,
        )

        return self.properties.get("transcription", CallTranscriptionInfo())

    @property
    def audio_routing_groups(self) -> EntityCollection[AudioRoutingGroup]:
        """Gets the audioRoutingGroups property"""
        from office365.communications.calls.audio_routing_group import AudioRoutingGroup

        return self.properties.get(
            "audioRoutingGroups",
            EntityCollection[AudioRoutingGroup](
                self.context, AudioRoutingGroup, ResourcePath("audioRoutingGroups", self.resource_path)
            ),
        )

    @property
    def content_sharing_sessions(self) -> EntityCollection[ContentSharingSession]:
        """Gets the contentSharingSessions property"""
        from office365.communications.calls.content_sharing_session import (
            ContentSharingSession,
        )

        return self.properties.get(
            "contentSharingSessions",
            EntityCollection[ContentSharingSession](
                self.context, ContentSharingSession, ResourcePath("contentSharingSessions", self.resource_path)
            ),
        )
