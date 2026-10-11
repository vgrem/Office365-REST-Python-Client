from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )
    from office365.intune.devices.configurations.applisttype import AppListType
    from office365.intune.devices.management.mobileapps.app_list_item import AppListItem


class MacOSGeneralDeviceConfiguration(Entity):
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
    def email_in_domain_suffixes(self) -> StringCollection:
        """Gets the emailInDomainSuffixes property"""
        return self.properties.get("emailInDomainSuffixes", StringCollection())

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
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSGeneralDeviceConfiguration"
