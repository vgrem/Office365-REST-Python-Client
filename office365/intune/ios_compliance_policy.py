from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )
    from office365.intune.devices.threatprotectionlevel import (
        DeviceThreatProtectionLevel,
    )


class IosCompliancePolicy(Entity):
    @property
    def device_threat_protection_enabled(self) -> Optional[bool]:
        """Gets the deviceThreatProtectionEnabled property"""
        return self.properties.get("deviceThreatProtectionEnabled", None)

    @property
    def device_threat_protection_required_security_level(self) -> DeviceThreatProtectionLevel:
        """Gets the deviceThreatProtectionRequiredSecurityLevel property"""
        from office365.intune.devices.threatprotectionlevel import (
            DeviceThreatProtectionLevel,
        )

        return self.properties.get(
            "deviceThreatProtectionRequiredSecurityLevel", DeviceThreatProtectionLevel.unavailable
        )

    @property
    def managed_email_profile_required(self) -> Optional[bool]:
        """Gets the managedEmailProfileRequired property"""
        return self.properties.get("managedEmailProfileRequired", None)

    @property
    def os_maximum_version(self) -> Optional[str]:
        """Gets the osMaximumVersion property"""
        return self.properties.get("osMaximumVersion", None)

    @property
    def os_minimum_version(self) -> Optional[str]:
        """Gets the osMinimumVersion property"""
        return self.properties.get("osMinimumVersion", None)

    @property
    def passcode_block_simple(self) -> Optional[bool]:
        """Gets the passcodeBlockSimple property"""
        return self.properties.get("passcodeBlockSimple", None)

    @property
    def passcode_expiration_days(self) -> Optional[int]:
        """Gets the passcodeExpirationDays property"""
        return self.properties.get("passcodeExpirationDays", None)

    @property
    def passcode_minimum_character_set_count(self) -> Optional[int]:
        """Gets the passcodeMinimumCharacterSetCount property"""
        return self.properties.get("passcodeMinimumCharacterSetCount", None)

    @property
    def passcode_minimum_length(self) -> Optional[int]:
        """Gets the passcodeMinimumLength property"""
        return self.properties.get("passcodeMinimumLength", None)

    @property
    def passcode_minutes_of_inactivity_before_lock(self) -> Optional[int]:
        """Gets the passcodeMinutesOfInactivityBeforeLock property"""
        return self.properties.get("passcodeMinutesOfInactivityBeforeLock", None)

    @property
    def passcode_previous_passcode_block_count(self) -> Optional[int]:
        """Gets the passcodePreviousPasscodeBlockCount property"""
        return self.properties.get("passcodePreviousPasscodeBlockCount", None)

    @property
    def passcode_required(self) -> Optional[bool]:
        """Gets the passcodeRequired property"""
        return self.properties.get("passcodeRequired", None)

    @property
    def passcode_required_type(self) -> RequiredPasswordType:
        """Gets the passcodeRequiredType property"""
        from office365.intune.devices.compliance.requiredpasswordtype import (
            RequiredPasswordType,
        )

        return self.properties.get("passcodeRequiredType", RequiredPasswordType.deviceDefault)

    @property
    def security_block_jailbroken_devices(self) -> Optional[bool]:
        """Gets the securityBlockJailbrokenDevices property"""
        return self.properties.get("securityBlockJailbrokenDevices", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosCompliancePolicy"
