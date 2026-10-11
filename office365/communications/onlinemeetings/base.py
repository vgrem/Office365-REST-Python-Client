from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.communications.meetings.chathistorydefaultmode import (
    MeetingChatHistoryDefaultMode,
)
from office365.communications.meetings.chatmode import MeetingChatMode
from office365.communications.meetings.liveshareoptions import MeetingLiveShareOptions
from office365.communications.onlinemeetings.allowedlobbyadmitterroles import (
    AllowedLobbyAdmitterRoles,
)
from office365.communications.onlinemeetings.lobby_bypass_settings import (
    LobbyBypassSettings,
)
from office365.communications.onlinemeetings.online_meeting_type import (
    OnlineMeetingType,
)
from office365.communications.onlinemeetings.presenters import OnlineMeetingPresenters
from office365.communications.onlinemeetings.watermark_protection_values import (
    WatermarkProtectionValues,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.audio_conferencing import AudioConferencing
    from office365.communications.chat_restrictions import ChatRestrictions
    from office365.communications.join_meeting_id_settings import JoinMeetingIdSettings
    from office365.communications.onlinemeetings.collection import ChatInfo
    from office365.communications.onlinemeetings.meeting_attendance_report import (
        MeetingAttendanceReport,
    )
    from office365.communications.onlinemeetings.sensitivity_label_assignment import (
        OnlineMeetingSensitivityLabelAssignment,
    )
    from office365.security.cloud_video_interop_info import (
        CloudVideoInteropInfo,
    )


class OnlineMeetingBase(Entity):
    """Represents a base online meeting. The base type of onlineMeeting and virtualEventSession."""

    @property
    def allow_attendee_to_enable_camera(self) -> Optional[bool]:
        """Indicates whether attendees can turn on their camera."""
        return self.properties.get("allowAttendeeToEnableCamera", None)

    @property
    def allow_attendee_to_enable_mic(self) -> Optional[bool]:
        """Indicates whether attendees can turn on their microphone."""
        return self.properties.get("allowAttendeeToEnableMic", None)

    @property
    def allow_breakout_rooms(self) -> Optional[bool]:
        """Indicates whether breakout rooms are enabled for the meeting."""
        return self.properties.get("allowBreakoutRooms", None)

    @property
    def allow_copying_and_sharing_meeting_content(self) -> Optional[bool]:
        """Gets the allowCopyingAndSharingMeetingContent property"""
        return self.properties.get("allowCopyingAndSharingMeetingContent", None)

    @property
    def allowed_lobby_admitters(self) -> AllowedLobbyAdmitterRoles:
        """Gets the allowedLobbyAdmitters property"""
        return self.properties.get(
            "allowedLobbyAdmitters", AllowedLobbyAdmitterRoles.organizerAndCoOrganizersAndPresenters
        )

    @property
    def allowed_presenters(self) -> OnlineMeetingPresenters:
        """Gets the allowedPresenters property"""
        return self.properties.get("allowedPresenters", OnlineMeetingPresenters.everyone)

    @property
    def allow_live_share(self) -> MeetingLiveShareOptions:
        """Gets the allowLiveShare property"""
        return self.properties.get("allowLiveShare", MeetingLiveShareOptions.enabled)

    @property
    def allow_meeting_chat(self) -> MeetingChatMode:
        """Gets the allowMeetingChat property"""
        return self.properties.get("allowMeetingChat", MeetingChatMode.enabled)

    @property
    def allow_participants_to_change_name(self) -> Optional[bool]:
        """Gets the allowParticipantsToChangeName property"""
        return self.properties.get("allowParticipantsToChangeName", None)

    @property
    def allow_power_point_sharing(self) -> Optional[bool]:
        """Gets the allowPowerPointSharing property"""
        return self.properties.get("allowPowerPointSharing", None)

    @property
    def allow_recording(self) -> Optional[bool]:
        """Gets the allowRecording property"""
        return self.properties.get("allowRecording", None)

    @property
    def allow_teamwork_reactions(self) -> Optional[bool]:
        """Gets the allowTeamworkReactions property"""
        return self.properties.get("allowTeamworkReactions", None)

    @property
    def allow_transcription(self) -> Optional[bool]:
        """Gets the allowTranscription property"""
        return self.properties.get("allowTranscription", None)

    @property
    def allow_whiteboard(self) -> Optional[bool]:
        """Gets the allowWhiteboard property"""
        return self.properties.get("allowWhiteboard", None)

    @property
    def chat_info(self) -> "ChatInfo":
        """Gets the chatInfo property"""
        from office365.communications.onlinemeetings.collection import ChatInfo

        return self.properties.get("chatInfo", ChatInfo())

    @property
    def expiry_date_time(self) -> Optional[datetime]:
        """Gets the expiryDateTime property"""
        return self.properties.get("expiryDateTime", datetime.min)

    @property
    def is_end_to_end_encryption_enabled(self) -> Optional[bool]:
        """Gets the isEndToEndEncryptionEnabled property"""
        return self.properties.get("isEndToEndEncryptionEnabled", None)

    @property
    def is_entry_exit_announced(self) -> Optional[bool]:
        """Gets the isEntryExitAnnounced property"""
        return self.properties.get("isEntryExitAnnounced", None)

    @property
    def join_information(self) -> ItemBody:
        """Gets the joinInformation property"""
        return self.properties.get("joinInformation", ItemBody())

    @property
    def join_web_url(self) -> Optional[str]:
        """Gets the joinWebUrl property"""
        return self.properties.get("joinWebUrl", None)

    @property
    def lobby_bypass_settings(self) -> LobbyBypassSettings:
        """Gets the lobbyBypassSettings property"""
        return self.properties.get("lobbyBypassSettings", LobbyBypassSettings())

    @property
    def meeting_options_web_url(self) -> Optional[str]:
        """Gets the meetingOptionsWebUrl property"""
        return self.properties.get("meetingOptionsWebUrl", None)

    @property
    def meeting_spoken_language_tag(self) -> Optional[str]:
        """Gets the meetingSpokenLanguageTag property"""
        return self.properties.get("meetingSpokenLanguageTag", None)

    @property
    def meeting_type(self) -> OnlineMeetingType:
        """Gets the meetingType property"""
        return self.properties.get("meetingType", OnlineMeetingType.adhoc)

    @property
    def record_automatically(self) -> Optional[bool]:
        """Gets the recordAutomatically property"""
        return self.properties.get("recordAutomatically", None)

    @property
    def share_meeting_chat_history_default(self) -> MeetingChatHistoryDefaultMode:
        """Gets the shareMeetingChatHistoryDefault property"""
        return self.properties.get("shareMeetingChatHistoryDefault", MeetingChatHistoryDefaultMode.none)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def video_teleconference_id(self) -> Optional[str]:
        """Gets the videoTeleconferenceId property"""
        return self.properties.get("videoTeleconferenceId", None)

    @property
    def watermark_protection(self) -> WatermarkProtectionValues:
        """Gets the watermarkProtection property"""
        return self.properties.get("watermarkProtection", WatermarkProtectionValues())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnlineMeetingBase"

    @property
    def audio_conferencing(self) -> AudioConferencing:
        """Gets the audioConferencing property"""
        from office365.communications.audio_conferencing import AudioConferencing

        return self.properties.get("audioConferencing", AudioConferencing())

    @property
    def chat_restrictions(self) -> ChatRestrictions:
        """Gets the chatRestrictions property"""
        from office365.communications.chat_restrictions import ChatRestrictions

        return self.properties.get("chatRestrictions", ChatRestrictions())

    @property
    def cloud_video_interop_info(self) -> CloudVideoInteropInfo:
        """Gets the cloudVideoInteropInfo property"""
        from office365.security.cloud_video_interop_info import (
            CloudVideoInteropInfo,
        )

        return self.properties.get("cloudVideoInteropInfo", CloudVideoInteropInfo())

    @property
    def join_meeting_id_settings(self) -> JoinMeetingIdSettings:
        """Gets the joinMeetingIdSettings property"""
        from office365.communications.join_meeting_id_settings import (
            JoinMeetingIdSettings,
        )

        return self.properties.get("joinMeetingIdSettings", JoinMeetingIdSettings())

    @property
    def sensitivity_label_assignment(self) -> OnlineMeetingSensitivityLabelAssignment:
        """Gets the sensitivityLabelAssignment property"""
        from office365.communications.onlinemeetings.sensitivity_label_assignment import (
            OnlineMeetingSensitivityLabelAssignment,
        )

        return self.properties.get("sensitivityLabelAssignment", OnlineMeetingSensitivityLabelAssignment())

    @property
    def attendance_reports(self) -> EntityCollection[MeetingAttendanceReport]:
        """Gets the attendanceReports property"""
        from office365.communications.onlinemeetings.meeting_attendance_report import (
            MeetingAttendanceReport,
        )

        return self.properties.get(
            "attendanceReports",
            EntityCollection[MeetingAttendanceReport](
                self.context, MeetingAttendanceReport, ResourcePath("attendanceReports", self.resource_path)
            ),
        )
