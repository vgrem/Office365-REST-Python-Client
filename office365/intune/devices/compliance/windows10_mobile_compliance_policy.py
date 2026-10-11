from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )


class Windows10MobileCompliancePolicy(Entity):
    @property
    def bit_locker_enabled(self) -> Optional[bool]:
        """Gets the bitLockerEnabled property"""
        return self.properties.get("bitLockerEnabled", None)

    @property
    def code_integrity_enabled(self) -> Optional[bool]:
        """Gets the codeIntegrityEnabled property"""
        return self.properties.get("codeIntegrityEnabled", None)

    @property
    def early_launch_anti_malware_driver_enabled(self) -> Optional[bool]:
        """Gets the earlyLaunchAntiMalwareDriverEnabled property"""
        return self.properties.get("earlyLaunchAntiMalwareDriverEnabled", None)

    @property
    def os_maximum_version(self) -> Optional[str]:
        """Gets the osMaximumVersion property"""
        return self.properties.get("osMaximumVersion", None)

    @property
    def os_minimum_version(self) -> Optional[str]:
        """Gets the osMinimumVersion property"""
        return self.properties.get("osMinimumVersion", None)

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
    def password_minutes_of_inactivity_before_lock(self) -> Optional[int]:
        """Gets the passwordMinutesOfInactivityBeforeLock property"""
        return self.properties.get("passwordMinutesOfInactivityBeforeLock", None)

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
    def password_require_to_unlock_from_idle(self) -> Optional[bool]:
        """Gets the passwordRequireToUnlockFromIdle property"""
        return self.properties.get("passwordRequireToUnlockFromIdle", None)

    @property
    def secure_boot_enabled(self) -> Optional[bool]:
        """Gets the secureBootEnabled property"""
        return self.properties.get("secureBootEnabled", None)

    @property
    def storage_require_encryption(self) -> Optional[bool]:
        """Gets the storageRequireEncryption property"""
        return self.properties.get("storageRequireEncryption", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows10MobileCompliancePolicy"
