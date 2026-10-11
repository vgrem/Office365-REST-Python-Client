from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )
    from office365.intune.devices.configurations.applisttype import AppListType
    from office365.intune.devices.management.mobileapps.app_list_item import AppListItem


class WindowsPhone81GeneralConfiguration(Entity):
    @property
    def apply_only_to_windows_phone81(self) -> Optional[bool]:
        """Gets the applyOnlyToWindowsPhone81 property"""
        return self.properties.get("applyOnlyToWindowsPhone81", None)

    @property
    def apps_block_copy_paste(self) -> Optional[bool]:
        """Gets the appsBlockCopyPaste property"""
        return self.properties.get("appsBlockCopyPaste", None)

    @property
    def bluetooth_blocked(self) -> Optional[bool]:
        """Gets the bluetoothBlocked property"""
        return self.properties.get("bluetoothBlocked", None)

    @property
    def camera_blocked(self) -> Optional[bool]:
        """Gets the cameraBlocked property"""
        return self.properties.get("cameraBlocked", None)

    @property
    def cellular_block_wifi_tethering(self) -> Optional[bool]:
        """Gets the cellularBlockWifiTethering property"""
        return self.properties.get("cellularBlockWifiTethering", None)

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
    def diagnostic_data_block_submission(self) -> Optional[bool]:
        """Gets the diagnosticDataBlockSubmission property"""
        return self.properties.get("diagnosticDataBlockSubmission", None)

    @property
    def email_block_adding_accounts(self) -> Optional[bool]:
        """Gets the emailBlockAddingAccounts property"""
        return self.properties.get("emailBlockAddingAccounts", None)

    @property
    def location_services_blocked(self) -> Optional[bool]:
        """Gets the locationServicesBlocked property"""
        return self.properties.get("locationServicesBlocked", None)

    @property
    def microsoft_account_blocked(self) -> Optional[bool]:
        """Gets the microsoftAccountBlocked property"""
        return self.properties.get("microsoftAccountBlocked", None)

    @property
    def nfc_blocked(self) -> Optional[bool]:
        """Gets the nfcBlocked property"""
        return self.properties.get("nfcBlocked", None)

    @property
    def password_block_simple(self) -> Optional[bool]:
        """Gets the passwordBlockSimple property"""
        return self.properties.get("passwordBlockSimple", None)

    @property
    def password_expiration_days(self) -> Optional[int]:
        """Gets the passwordExpirationDays property"""
        return self.properties.get("passwordExpirationDays", None)

    @property
    def password_minimum_character_set_count(self) -> Optional[int]:
        """Gets the passwordMinimumCharacterSetCount property"""
        return self.properties.get("passwordMinimumCharacterSetCount", None)

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
    def password_required_type(self) -> RequiredPasswordType:
        """Gets the passwordRequiredType property"""
        from office365.intune.devices.compliance.requiredpasswordtype import (
            RequiredPasswordType,
        )

        return self.properties.get("passwordRequiredType", RequiredPasswordType.deviceDefault)

    @property
    def password_sign_in_failure_count_before_factory_reset(self) -> Optional[int]:
        """Gets the passwordSignInFailureCountBeforeFactoryReset property"""
        return self.properties.get("passwordSignInFailureCountBeforeFactoryReset", None)

    @property
    def screen_capture_blocked(self) -> Optional[bool]:
        """Gets the screenCaptureBlocked property"""
        return self.properties.get("screenCaptureBlocked", None)

    @property
    def storage_block_removable_storage(self) -> Optional[bool]:
        """Gets the storageBlockRemovableStorage property"""
        return self.properties.get("storageBlockRemovableStorage", None)

    @property
    def storage_require_encryption(self) -> Optional[bool]:
        """Gets the storageRequireEncryption property"""
        return self.properties.get("storageRequireEncryption", None)

    @property
    def web_browser_blocked(self) -> Optional[bool]:
        """Gets the webBrowserBlocked property"""
        return self.properties.get("webBrowserBlocked", None)

    @property
    def wifi_block_automatic_connect_hotspots(self) -> Optional[bool]:
        """Gets the wifiBlockAutomaticConnectHotspots property"""
        return self.properties.get("wifiBlockAutomaticConnectHotspots", None)

    @property
    def wifi_blocked(self) -> Optional[bool]:
        """Gets the wifiBlocked property"""
        return self.properties.get("wifiBlocked", None)

    @property
    def wifi_block_hotspot_reporting(self) -> Optional[bool]:
        """Gets the wifiBlockHotspotReporting property"""
        return self.properties.get("wifiBlockHotspotReporting", None)

    @property
    def windows_store_blocked(self) -> Optional[bool]:
        """Gets the windowsStoreBlocked property"""
        return self.properties.get("windowsStoreBlocked", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsPhone81GeneralConfiguration"
