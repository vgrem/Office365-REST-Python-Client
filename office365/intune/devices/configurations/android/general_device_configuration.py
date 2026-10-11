from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.androidrequiredpasswordtype import (
        AndroidRequiredPasswordType,
    )
    from office365.intune.devices.configurations.applisttype import AppListType
    from office365.intune.devices.configurations.webbrowsercookiesettings import (
        WebBrowserCookieSettings,
    )
    from office365.intune.devices.management.mobileapps.app_list_item import AppListItem


class AndroidGeneralDeviceConfiguration(Entity):
    @property
    def apps_block_clipboard_sharing(self) -> Optional[bool]:
        """Gets the appsBlockClipboardSharing property"""
        return self.properties.get("appsBlockClipboardSharing", None)

    @property
    def apps_block_copy_paste(self) -> Optional[bool]:
        """Gets the appsBlockCopyPaste property"""
        return self.properties.get("appsBlockCopyPaste", None)

    @property
    def apps_block_you_tube(self) -> Optional[bool]:
        """Gets the appsBlockYouTube property"""
        return self.properties.get("appsBlockYouTube", None)

    @property
    def apps_hide_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the appsHideList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("appsHideList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def apps_install_allow_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the appsInstallAllowList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("appsInstallAllowList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def apps_launch_block_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the appsLaunchBlockList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("appsLaunchBlockList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def bluetooth_blocked(self) -> Optional[bool]:
        """Gets the bluetoothBlocked property"""
        return self.properties.get("bluetoothBlocked", None)

    @property
    def camera_blocked(self) -> Optional[bool]:
        """Gets the cameraBlocked property"""
        return self.properties.get("cameraBlocked", None)

    @property
    def cellular_block_data_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockDataRoaming property"""
        return self.properties.get("cellularBlockDataRoaming", None)

    @property
    def cellular_block_messaging(self) -> Optional[bool]:
        """Gets the cellularBlockMessaging property"""
        return self.properties.get("cellularBlockMessaging", None)

    @property
    def cellular_block_voice_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockVoiceRoaming property"""
        return self.properties.get("cellularBlockVoiceRoaming", None)

    @property
    def cellular_block_wi_fi_tethering(self) -> Optional[bool]:
        """Gets the cellularBlockWiFiTethering property"""
        return self.properties.get("cellularBlockWiFiTethering", None)

    @property
    def compliant_app_list_type(self) -> AppListType:
        """Gets the compliantAppListType property"""
        from office365.intune.devices.configurations.applisttype import AppListType

        return self.properties.get("compliantAppListType", AppListType.none)

    @property
    def compliant_apps_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the compliantAppsList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("compliantAppsList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def device_sharing_allowed(self) -> Optional[bool]:
        """Gets the deviceSharingAllowed property"""
        return self.properties.get("deviceSharingAllowed", None)

    @property
    def diagnostic_data_block_submission(self) -> Optional[bool]:
        """Gets the diagnosticDataBlockSubmission property"""
        return self.properties.get("diagnosticDataBlockSubmission", None)

    @property
    def factory_reset_blocked(self) -> Optional[bool]:
        """Gets the factoryResetBlocked property"""
        return self.properties.get("factoryResetBlocked", None)

    @property
    def google_account_block_auto_sync(self) -> Optional[bool]:
        """Gets the googleAccountBlockAutoSync property"""
        return self.properties.get("googleAccountBlockAutoSync", None)

    @property
    def google_play_store_blocked(self) -> Optional[bool]:
        """Gets the googlePlayStoreBlocked property"""
        return self.properties.get("googlePlayStoreBlocked", None)

    @property
    def kiosk_mode_apps(self) -> ClientValueCollection[AppListItem]:
        """Gets the kioskModeApps property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("kioskModeApps", ClientValueCollection[AppListItem](AppListItem))

    @property
    def kiosk_mode_block_sleep_button(self) -> Optional[bool]:
        """Gets the kioskModeBlockSleepButton property"""
        return self.properties.get("kioskModeBlockSleepButton", None)

    @property
    def kiosk_mode_block_volume_buttons(self) -> Optional[bool]:
        """Gets the kioskModeBlockVolumeButtons property"""
        return self.properties.get("kioskModeBlockVolumeButtons", None)

    @property
    def location_services_blocked(self) -> Optional[bool]:
        """Gets the locationServicesBlocked property"""
        return self.properties.get("locationServicesBlocked", None)

    @property
    def nfc_blocked(self) -> Optional[bool]:
        """Gets the nfcBlocked property"""
        return self.properties.get("nfcBlocked", None)

    @property
    def password_block_fingerprint_unlock(self) -> Optional[bool]:
        """Gets the passwordBlockFingerprintUnlock property"""
        return self.properties.get("passwordBlockFingerprintUnlock", None)

    @property
    def password_block_trust_agents(self) -> Optional[bool]:
        """Gets the passwordBlockTrustAgents property"""
        return self.properties.get("passwordBlockTrustAgents", None)

    @property
    def password_expiration_days(self) -> Optional[int]:
        """Gets the passwordExpirationDays property"""
        return self.properties.get("passwordExpirationDays", None)

    @property
    def password_minimum_length(self) -> Optional[int]:
        """Gets the passwordMinimumLength property"""
        return self.properties.get("passwordMinimumLength", None)

    @property
    def password_minutes_of_inactivity_before_screen_timeout(self) -> Optional[int]:
        """Gets the passwordMinutesOfInactivityBeforeScreenTimeout property"""
        return self.properties.get("passwordMinutesOfInactivityBeforeScreenTimeout", None)

    @property
    def password_previous_password_block_count(self) -> Optional[int]:
        """Gets the passwordPreviousPasswordBlockCount property"""
        return self.properties.get("passwordPreviousPasswordBlockCount", None)

    @property
    def password_required(self) -> Optional[bool]:
        """Gets the passwordRequired property"""
        return self.properties.get("passwordRequired", None)

    @property
    def password_required_type(self) -> AndroidRequiredPasswordType:
        """Gets the passwordRequiredType property"""
        from office365.intune.devices.compliance.androidrequiredpasswordtype import (
            AndroidRequiredPasswordType,
        )

        return self.properties.get("passwordRequiredType", AndroidRequiredPasswordType.deviceDefault)

    @property
    def password_sign_in_failure_count_before_factory_reset(self) -> Optional[int]:
        """Gets the passwordSignInFailureCountBeforeFactoryReset property"""
        return self.properties.get("passwordSignInFailureCountBeforeFactoryReset", None)

    @property
    def power_off_blocked(self) -> Optional[bool]:
        """Gets the powerOffBlocked property"""
        return self.properties.get("powerOffBlocked", None)

    @property
    def screen_capture_blocked(self) -> Optional[bool]:
        """Gets the screenCaptureBlocked property"""
        return self.properties.get("screenCaptureBlocked", None)

    @property
    def security_require_verify_apps(self) -> Optional[bool]:
        """Gets the securityRequireVerifyApps property"""
        return self.properties.get("securityRequireVerifyApps", None)

    @property
    def storage_block_google_backup(self) -> Optional[bool]:
        """Gets the storageBlockGoogleBackup property"""
        return self.properties.get("storageBlockGoogleBackup", None)

    @property
    def storage_block_removable_storage(self) -> Optional[bool]:
        """Gets the storageBlockRemovableStorage property"""
        return self.properties.get("storageBlockRemovableStorage", None)

    @property
    def storage_require_device_encryption(self) -> Optional[bool]:
        """Gets the storageRequireDeviceEncryption property"""
        return self.properties.get("storageRequireDeviceEncryption", None)

    @property
    def storage_require_removable_storage_encryption(self) -> Optional[bool]:
        """Gets the storageRequireRemovableStorageEncryption property"""
        return self.properties.get("storageRequireRemovableStorageEncryption", None)

    @property
    def voice_assistant_blocked(self) -> Optional[bool]:
        """Gets the voiceAssistantBlocked property"""
        return self.properties.get("voiceAssistantBlocked", None)

    @property
    def voice_dialing_blocked(self) -> Optional[bool]:
        """Gets the voiceDialingBlocked property"""
        return self.properties.get("voiceDialingBlocked", None)

    @property
    def web_browser_block_autofill(self) -> Optional[bool]:
        """Gets the webBrowserBlockAutofill property"""
        return self.properties.get("webBrowserBlockAutofill", None)

    @property
    def web_browser_blocked(self) -> Optional[bool]:
        """Gets the webBrowserBlocked property"""
        return self.properties.get("webBrowserBlocked", None)

    @property
    def web_browser_block_java_script(self) -> Optional[bool]:
        """Gets the webBrowserBlockJavaScript property"""
        return self.properties.get("webBrowserBlockJavaScript", None)

    @property
    def web_browser_block_popups(self) -> Optional[bool]:
        """Gets the webBrowserBlockPopups property"""
        return self.properties.get("webBrowserBlockPopups", None)

    @property
    def web_browser_cookie_settings(self) -> WebBrowserCookieSettings:
        """Gets the webBrowserCookieSettings property"""
        from office365.intune.devices.configurations.webbrowsercookiesettings import (
            WebBrowserCookieSettings,
        )

        return self.properties.get("webBrowserCookieSettings", WebBrowserCookieSettings.browserDefault)

    @property
    def wi_fi_blocked(self) -> Optional[bool]:
        """Gets the wiFiBlocked property"""
        return self.properties.get("wiFiBlocked", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AndroidGeneralDeviceConfiguration"
