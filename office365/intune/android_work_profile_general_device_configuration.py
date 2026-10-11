from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.android.workprofilecrossprofiledatasharingtype import (
        AndroidWorkProfileCrossProfileDataSharingType,
    )
    from office365.intune.devices.configurations.android.workprofiledefaultapppermissionpolicytype import (
        AndroidWorkProfileDefaultAppPermissionPolicyType,
    )
    from office365.intune.devices.configurations.android.workprofilerequiredpasswordtype import (
        AndroidWorkProfileRequiredPasswordType,
    )


class AndroidWorkProfileGeneralDeviceConfiguration(Entity):
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
    def password_required_type(self) -> AndroidWorkProfileRequiredPasswordType:
        """Gets the passwordRequiredType property"""
        from office365.intune.devices.configurations.android.workprofilerequiredpasswordtype import (
            AndroidWorkProfileRequiredPasswordType,
        )

        return self.properties.get("passwordRequiredType", AndroidWorkProfileRequiredPasswordType.deviceDefault)

    @property
    def password_sign_in_failure_count_before_factory_reset(self) -> Optional[int]:
        """Gets the passwordSignInFailureCountBeforeFactoryReset property"""
        return self.properties.get("passwordSignInFailureCountBeforeFactoryReset", None)

    @property
    def security_require_verify_apps(self) -> Optional[bool]:
        """Gets the securityRequireVerifyApps property"""
        return self.properties.get("securityRequireVerifyApps", None)

    @property
    def work_profile_block_adding_accounts(self) -> Optional[bool]:
        """Gets the workProfileBlockAddingAccounts property"""
        return self.properties.get("workProfileBlockAddingAccounts", None)

    @property
    def work_profile_block_camera(self) -> Optional[bool]:
        """Gets the workProfileBlockCamera property"""
        return self.properties.get("workProfileBlockCamera", None)

    @property
    def work_profile_block_cross_profile_caller_id(self) -> Optional[bool]:
        """Gets the workProfileBlockCrossProfileCallerId property"""
        return self.properties.get("workProfileBlockCrossProfileCallerId", None)

    @property
    def work_profile_block_cross_profile_contacts_search(self) -> Optional[bool]:
        """Gets the workProfileBlockCrossProfileContactsSearch property"""
        return self.properties.get("workProfileBlockCrossProfileContactsSearch", None)

    @property
    def work_profile_block_cross_profile_copy_paste(self) -> Optional[bool]:
        """Gets the workProfileBlockCrossProfileCopyPaste property"""
        return self.properties.get("workProfileBlockCrossProfileCopyPaste", None)

    @property
    def work_profile_block_notifications_while_device_locked(self) -> Optional[bool]:
        """Gets the workProfileBlockNotificationsWhileDeviceLocked property"""
        return self.properties.get("workProfileBlockNotificationsWhileDeviceLocked", None)

    @property
    def work_profile_block_screen_capture(self) -> Optional[bool]:
        """Gets the workProfileBlockScreenCapture property"""
        return self.properties.get("workProfileBlockScreenCapture", None)

    @property
    def work_profile_bluetooth_enable_contact_sharing(self) -> Optional[bool]:
        """Gets the workProfileBluetoothEnableContactSharing property"""
        return self.properties.get("workProfileBluetoothEnableContactSharing", None)

    @property
    def work_profile_data_sharing_type(self) -> AndroidWorkProfileCrossProfileDataSharingType:
        """Gets the workProfileDataSharingType property"""
        from office365.intune.devices.configurations.android.workprofilecrossprofiledatasharingtype import (
            AndroidWorkProfileCrossProfileDataSharingType,
        )

        return self.properties.get(
            "workProfileDataSharingType", AndroidWorkProfileCrossProfileDataSharingType.deviceDefault
        )

    @property
    def work_profile_default_app_permission_policy(self) -> AndroidWorkProfileDefaultAppPermissionPolicyType:
        """Gets the workProfileDefaultAppPermissionPolicy property"""
        from office365.intune.devices.configurations.android.workprofiledefaultapppermissionpolicytype import (
            AndroidWorkProfileDefaultAppPermissionPolicyType,
        )

        return self.properties.get(
            "workProfileDefaultAppPermissionPolicy", AndroidWorkProfileDefaultAppPermissionPolicyType.deviceDefault
        )

    @property
    def work_profile_password_block_fingerprint_unlock(self) -> Optional[bool]:
        """Gets the workProfilePasswordBlockFingerprintUnlock property"""
        return self.properties.get("workProfilePasswordBlockFingerprintUnlock", None)

    @property
    def work_profile_password_block_trust_agents(self) -> Optional[bool]:
        """Gets the workProfilePasswordBlockTrustAgents property"""
        return self.properties.get("workProfilePasswordBlockTrustAgents", None)

    @property
    def work_profile_password_expiration_days(self) -> Optional[int]:
        """Gets the workProfilePasswordExpirationDays property"""
        return self.properties.get("workProfilePasswordExpirationDays", None)

    @property
    def work_profile_password_minimum_length(self) -> Optional[int]:
        """Gets the workProfilePasswordMinimumLength property"""
        return self.properties.get("workProfilePasswordMinimumLength", None)

    @property
    def work_profile_password_min_letter_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinLetterCharacters property"""
        return self.properties.get("workProfilePasswordMinLetterCharacters", None)

    @property
    def work_profile_password_min_lower_case_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinLowerCaseCharacters property"""
        return self.properties.get("workProfilePasswordMinLowerCaseCharacters", None)

    @property
    def work_profile_password_min_non_letter_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinNonLetterCharacters property"""
        return self.properties.get("workProfilePasswordMinNonLetterCharacters", None)

    @property
    def work_profile_password_min_numeric_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinNumericCharacters property"""
        return self.properties.get("workProfilePasswordMinNumericCharacters", None)

    @property
    def work_profile_password_min_symbol_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinSymbolCharacters property"""
        return self.properties.get("workProfilePasswordMinSymbolCharacters", None)

    @property
    def work_profile_password_min_upper_case_characters(self) -> Optional[int]:
        """Gets the workProfilePasswordMinUpperCaseCharacters property"""
        return self.properties.get("workProfilePasswordMinUpperCaseCharacters", None)

    @property
    def work_profile_password_minutes_of_inactivity_before_screen_timeout(self) -> Optional[int]:
        """Gets the workProfilePasswordMinutesOfInactivityBeforeScreenTimeout property"""
        return self.properties.get("workProfilePasswordMinutesOfInactivityBeforeScreenTimeout", None)

    @property
    def work_profile_password_previous_password_block_count(self) -> Optional[int]:
        """Gets the workProfilePasswordPreviousPasswordBlockCount property"""
        return self.properties.get("workProfilePasswordPreviousPasswordBlockCount", None)

    @property
    def work_profile_password_required_type(self) -> AndroidWorkProfileRequiredPasswordType:
        """Gets the workProfilePasswordRequiredType property"""
        from office365.intune.devices.configurations.android.workprofilerequiredpasswordtype import (
            AndroidWorkProfileRequiredPasswordType,
        )

        return self.properties.get(
            "workProfilePasswordRequiredType", AndroidWorkProfileRequiredPasswordType.deviceDefault
        )

    @property
    def work_profile_password_sign_in_failure_count_before_factory_reset(self) -> Optional[int]:
        """Gets the workProfilePasswordSignInFailureCountBeforeFactoryReset property"""
        return self.properties.get("workProfilePasswordSignInFailureCountBeforeFactoryReset", None)

    @property
    def work_profile_require_password(self) -> Optional[bool]:
        """Gets the workProfileRequirePassword property"""
        return self.properties.get("workProfileRequirePassword", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AndroidWorkProfileGeneralDeviceConfiguration"
