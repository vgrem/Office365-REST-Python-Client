from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.windows.miracastchannel import (
        MiracastChannel,
    )
    from office365.intune.devices.configurations.windows.welcomescreenmeetinginformation import (
        WelcomeScreenMeetingInformation,
    )


class Windows10TeamGeneralConfiguration(Entity):
    @property
    def azure_operational_insights_block_telemetry(self) -> Optional[bool]:
        """Gets the azureOperationalInsightsBlockTelemetry property"""
        return self.properties.get("azureOperationalInsightsBlockTelemetry", None)

    @property
    def azure_operational_insights_workspace_id(self) -> Optional[str]:
        """Gets the azureOperationalInsightsWorkspaceId property"""
        return self.properties.get("azureOperationalInsightsWorkspaceId", None)

    @property
    def azure_operational_insights_workspace_key(self) -> Optional[str]:
        """Gets the azureOperationalInsightsWorkspaceKey property"""
        return self.properties.get("azureOperationalInsightsWorkspaceKey", None)

    @property
    def connect_app_block_auto_launch(self) -> Optional[bool]:
        """Gets the connectAppBlockAutoLaunch property"""
        return self.properties.get("connectAppBlockAutoLaunch", None)

    @property
    def maintenance_window_blocked(self) -> Optional[bool]:
        """Gets the maintenanceWindowBlocked property"""
        return self.properties.get("maintenanceWindowBlocked", None)

    @property
    def maintenance_window_duration_in_hours(self) -> Optional[int]:
        """Gets the maintenanceWindowDurationInHours property"""
        return self.properties.get("maintenanceWindowDurationInHours", None)

    @property
    def maintenance_window_start_time(self) -> Optional[time]:
        """Gets the maintenanceWindowStartTime property"""
        return self.properties.get("maintenanceWindowStartTime", None)

    @property
    def miracast_blocked(self) -> Optional[bool]:
        """Gets the miracastBlocked property"""
        return self.properties.get("miracastBlocked", None)

    @property
    def miracast_channel(self) -> MiracastChannel:
        """Gets the miracastChannel property"""
        from office365.intune.devices.configurations.windows.miracastchannel import (
            MiracastChannel,
        )

        return self.properties.get("miracastChannel", MiracastChannel.userDefined)

    @property
    def miracast_require_pin(self) -> Optional[bool]:
        """Gets the miracastRequirePin property"""
        return self.properties.get("miracastRequirePin", None)

    @property
    def settings_block_my_meetings_and_files(self) -> Optional[bool]:
        """Gets the settingsBlockMyMeetingsAndFiles property"""
        return self.properties.get("settingsBlockMyMeetingsAndFiles", None)

    @property
    def settings_block_session_resume(self) -> Optional[bool]:
        """Gets the settingsBlockSessionResume property"""
        return self.properties.get("settingsBlockSessionResume", None)

    @property
    def settings_block_signin_suggestions(self) -> Optional[bool]:
        """Gets the settingsBlockSigninSuggestions property"""
        return self.properties.get("settingsBlockSigninSuggestions", None)

    @property
    def settings_default_volume(self) -> Optional[int]:
        """Gets the settingsDefaultVolume property"""
        return self.properties.get("settingsDefaultVolume", None)

    @property
    def settings_screen_timeout_in_minutes(self) -> Optional[int]:
        """Gets the settingsScreenTimeoutInMinutes property"""
        return self.properties.get("settingsScreenTimeoutInMinutes", None)

    @property
    def settings_session_timeout_in_minutes(self) -> Optional[int]:
        """Gets the settingsSessionTimeoutInMinutes property"""
        return self.properties.get("settingsSessionTimeoutInMinutes", None)

    @property
    def settings_sleep_timeout_in_minutes(self) -> Optional[int]:
        """Gets the settingsSleepTimeoutInMinutes property"""
        return self.properties.get("settingsSleepTimeoutInMinutes", None)

    @property
    def welcome_screen_background_image_url(self) -> Optional[str]:
        """Gets the welcomeScreenBackgroundImageUrl property"""
        return self.properties.get("welcomeScreenBackgroundImageUrl", None)

    @property
    def welcome_screen_block_automatic_wake_up(self) -> Optional[bool]:
        """Gets the welcomeScreenBlockAutomaticWakeUp property"""
        return self.properties.get("welcomeScreenBlockAutomaticWakeUp", None)

    @property
    def welcome_screen_meeting_information(self) -> WelcomeScreenMeetingInformation:
        """Gets the welcomeScreenMeetingInformation property"""
        from office365.intune.devices.configurations.windows.welcomescreenmeetinginformation import (
            WelcomeScreenMeetingInformation,
        )

        return self.properties.get("welcomeScreenMeetingInformation", WelcomeScreenMeetingInformation.userDefined)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows10TeamGeneralConfiguration"
