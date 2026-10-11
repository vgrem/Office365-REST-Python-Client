from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )
    from office365.intune.devices.configurations.windows.internetsitesecuritylevel import (
        InternetSiteSecurityLevel,
    )
    from office365.intune.devices.configurations.windows.sitesecuritylevel import (
        SiteSecurityLevel,
    )
    from office365.intune.devices.configurations.windows.useraccountcontrolsettings import (
        WindowsUserAccountControlSettings,
    )


class Windows81GeneralConfiguration(Entity):
    @property
    def accounts_block_adding_non_microsoft_account_email(self) -> Optional[bool]:
        """Gets the accountsBlockAddingNonMicrosoftAccountEmail property"""
        return self.properties.get("accountsBlockAddingNonMicrosoftAccountEmail", None)

    @property
    def apply_only_to_windows81(self) -> Optional[bool]:
        """Gets the applyOnlyToWindows81 property"""
        return self.properties.get("applyOnlyToWindows81", None)

    @property
    def browser_block_autofill(self) -> Optional[bool]:
        """Gets the browserBlockAutofill property"""
        return self.properties.get("browserBlockAutofill", None)

    @property
    def browser_block_automatic_detection_of_intranet_sites(self) -> Optional[bool]:
        """Gets the browserBlockAutomaticDetectionOfIntranetSites property"""
        return self.properties.get("browserBlockAutomaticDetectionOfIntranetSites", None)

    @property
    def browser_block_enterprise_mode_access(self) -> Optional[bool]:
        """Gets the browserBlockEnterpriseModeAccess property"""
        return self.properties.get("browserBlockEnterpriseModeAccess", None)

    @property
    def browser_block_java_script(self) -> Optional[bool]:
        """Gets the browserBlockJavaScript property"""
        return self.properties.get("browserBlockJavaScript", None)

    @property
    def browser_block_plugins(self) -> Optional[bool]:
        """Gets the browserBlockPlugins property"""
        return self.properties.get("browserBlockPlugins", None)

    @property
    def browser_block_popups(self) -> Optional[bool]:
        """Gets the browserBlockPopups property"""
        return self.properties.get("browserBlockPopups", None)

    @property
    def browser_block_sending_do_not_track_header(self) -> Optional[bool]:
        """Gets the browserBlockSendingDoNotTrackHeader property"""
        return self.properties.get("browserBlockSendingDoNotTrackHeader", None)

    @property
    def browser_block_single_word_entry_on_intranet_sites(self) -> Optional[bool]:
        """Gets the browserBlockSingleWordEntryOnIntranetSites property"""
        return self.properties.get("browserBlockSingleWordEntryOnIntranetSites", None)

    @property
    def browser_enterprise_mode_site_list_location(self) -> Optional[str]:
        """Gets the browserEnterpriseModeSiteListLocation property"""
        return self.properties.get("browserEnterpriseModeSiteListLocation", None)

    @property
    def browser_internet_security_level(self) -> InternetSiteSecurityLevel:
        """Gets the browserInternetSecurityLevel property"""
        from office365.intune.devices.configurations.windows.internetsitesecuritylevel import (
            InternetSiteSecurityLevel,
        )

        return self.properties.get("browserInternetSecurityLevel", InternetSiteSecurityLevel.userDefined)

    @property
    def browser_intranet_security_level(self) -> SiteSecurityLevel:
        """Gets the browserIntranetSecurityLevel property"""
        from office365.intune.devices.configurations.windows.sitesecuritylevel import (
            SiteSecurityLevel,
        )

        return self.properties.get("browserIntranetSecurityLevel", SiteSecurityLevel.userDefined)

    @property
    def browser_logging_report_location(self) -> Optional[str]:
        """Gets the browserLoggingReportLocation property"""
        return self.properties.get("browserLoggingReportLocation", None)

    @property
    def browser_require_firewall(self) -> Optional[bool]:
        """Gets the browserRequireFirewall property"""
        return self.properties.get("browserRequireFirewall", None)

    @property
    def browser_require_fraud_warning(self) -> Optional[bool]:
        """Gets the browserRequireFraudWarning property"""
        return self.properties.get("browserRequireFraudWarning", None)

    @property
    def browser_require_high_security_for_restricted_sites(self) -> Optional[bool]:
        """Gets the browserRequireHighSecurityForRestrictedSites property"""
        return self.properties.get("browserRequireHighSecurityForRestrictedSites", None)

    @property
    def browser_require_smart_screen(self) -> Optional[bool]:
        """Gets the browserRequireSmartScreen property"""
        return self.properties.get("browserRequireSmartScreen", None)

    @property
    def browser_trusted_sites_security_level(self) -> SiteSecurityLevel:
        """Gets the browserTrustedSitesSecurityLevel property"""
        from office365.intune.devices.configurations.windows.sitesecuritylevel import (
            SiteSecurityLevel,
        )

        return self.properties.get("browserTrustedSitesSecurityLevel", SiteSecurityLevel.userDefined)

    @property
    def cellular_block_data_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockDataRoaming property"""
        return self.properties.get("cellularBlockDataRoaming", None)

    @property
    def diagnostics_block_data_submission(self) -> Optional[bool]:
        """Gets the diagnosticsBlockDataSubmission property"""
        return self.properties.get("diagnosticsBlockDataSubmission", None)

    @property
    def password_block_picture_password_and_pin(self) -> Optional[bool]:
        """Gets the passwordBlockPicturePasswordAndPin property"""
        return self.properties.get("passwordBlockPicturePasswordAndPin", None)

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
    def storage_require_device_encryption(self) -> Optional[bool]:
        """Gets the storageRequireDeviceEncryption property"""
        return self.properties.get("storageRequireDeviceEncryption", None)

    @property
    def updates_require_automatic_updates(self) -> Optional[bool]:
        """Gets the updatesRequireAutomaticUpdates property"""
        return self.properties.get("updatesRequireAutomaticUpdates", None)

    @property
    def user_account_control_settings(self) -> WindowsUserAccountControlSettings:
        """Gets the userAccountControlSettings property"""
        from office365.intune.devices.configurations.windows.useraccountcontrolsettings import (
            WindowsUserAccountControlSettings,
        )

        return self.properties.get("userAccountControlSettings", WindowsUserAccountControlSettings.userDefined)

    @property
    def work_folders_url(self) -> Optional[str]:
        """Gets the workFoldersUrl property"""
        return self.properties.get("workFoldersUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows81GeneralConfiguration"
