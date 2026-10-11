from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from office365.communications.calls.invitation_participant_info import (
    InvitationParticipantInfo,
)
from office365.communications.calls.participant_info import ParticipantInfo
from office365.communications.onlinemeetings.restricted import OnlineMeetingRestricted
from office365.communications.operations.invite_participants import (
    InviteParticipantsOperation,
)
from office365.communications.operations.start_hold_music import StartHoldMusicOperation
from office365.communications.operations.stop_hold_music import StopHoldMusicOperation
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.communications.callrecords.media_stream import MediaStream
    from office365.communications.recording_info import RecordingInfo
    from office365.communications.removed_state import RemovedState


class Participant(Entity):
    """Represents a participant in a call."""

    def invite(self, participants: List[InvitationParticipantInfo], client_context: str) -> InviteParticipantsOperation:
        """Invite participants to the active call.

        Args:
            participants (list[InvitationParticipantInfo]): Unique Client Context string. Max limit is 256 chars.
            client_context (str): Unique Client Context string. Max limit is 256 chars.
        """
        return_type = InviteParticipantsOperation(self.context)
        payload = {
            "participants": ClientValueCollection(InvitationParticipantInfo, participants),
            "clientContext": client_context,
        }
        qry = ServiceOperationQuery(self, "invite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def start_hold_music(
        self, custom_prompt: Optional[str] = None, client_context: Optional[str] = None
    ) -> StartHoldMusicOperation:
        """Put a participant on hold and play music in the background.

        Args:
            custom_prompt (str or None): Audio prompt the participant will hear when placed on hold.
            client_context (str or None): Unique client context string. Can have a maximum of 256 characters.
        """
        return_type = StartHoldMusicOperation(self.context)
        payload = {"customPrompt": custom_prompt, "clientContext": client_context}
        qry = ServiceOperationQuery(self, "startHoldMusic", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def stop_hold_music(self, client_context: Optional[str] = None) -> StopHoldMusicOperation:
        """Reincorporate a participant previously put on hold to the call.

        Args:
            client_context (str or None): Unique client context string. Can have a maximum of 256 characters.
        """
        return_type = StopHoldMusicOperation(self.context)
        payload = {"clientContext": client_context}
        qry = ServiceOperationQuery(self, "stopHoldMusic", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def info(self) -> ParticipantInfo:
        """Information about the participant."""
        return self.properties.get("info", ParticipantInfo())

    @property
    def metadata(self) -> Optional[str]:
        """A blob of data provided by the participant in the roster."""
        return self.properties.get("metadata", None)

    @property
    def restricted_experience(self):
        """Information about the reason or reasons media content from a participant is restricted."""
        return self.properties.get("restrictedExperience", OnlineMeetingRestricted())

    @property
    def is_in_lobby(self) -> Optional[bool]:
        """Gets the isInLobby property"""
        return self.properties.get("isInLobby", None)

    @property
    def is_muted(self) -> Optional[bool]:
        """Gets the isMuted property"""
        return self.properties.get("isMuted", None)

    @property
    def media_streams(self) -> ClientValueCollection[MediaStream]:
        """Gets the mediaStreams property"""
        from office365.communications.callrecords.media_stream import MediaStream

        return self.properties.get("mediaStreams", ClientValueCollection[MediaStream](MediaStream))

    @property
    def recording_info(self) -> RecordingInfo:
        """Gets the recordingInfo property"""
        from office365.communications.recording_info import RecordingInfo

        return self.properties.get("recordingInfo", RecordingInfo())

    @property
    def removed_state(self) -> RemovedState:
        """Gets the removedState property"""
        from office365.communications.removed_state import RemovedState

        return self.properties.get("removedState", RemovedState())

    @property
    def roster_sequence_number(self) -> Optional[int]:
        """Gets the rosterSequenceNumber property"""
        return self.properties.get("rosterSequenceNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Participant"
