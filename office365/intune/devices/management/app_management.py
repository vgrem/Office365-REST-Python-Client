from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.devices.management.managed.app.registration import (
    ManagedAppRegistration,
)
from office365.intune.devices.management.managed.ebook.ebook import ManagedEBook
from office365.intune.devices.management.mobileapps.category import MobileAppCategory
from office365.intune.devices.management.mobileapps.mobile_app import MobileApp
from office365.intune.devices.management.mobileapps.relationship import (
    MobileAppRelationship,
)
from office365.intune.devices.management.vpptokens.vpp_token import VppToken
from office365.intune.policies.managed_app import ManagedAppPolicy
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.app.protections.android import (
        AndroidManagedAppProtection,
    )
    from office365.intune.devices.management.managed.app.protections.default import (
        DefaultManagedAppProtection,
    )
    from office365.intune.devices.management.managed.app.protections.ios import (
        IosManagedAppProtection,
    )
    from office365.intune.devices.management.managed.app.status import ManagedAppStatus
    from office365.intune.devices.management.managed.device_mobile_app_configuration import (
        ManagedDeviceMobileAppConfiguration,
    )
    from office365.intune.devices.management.mdm_windows_information_protection_policy import (
        MdmWindowsInformationProtectionPolicy,
    )
    from office365.intune.devices.management.targeted_managed_app_configuration import (
        TargetedManagedAppConfiguration,
    )
    from office365.intune.devices.management.windows_information_protection_policy import (
        WindowsInformationProtectionPolicy,
    )


class DeviceAppManagement(Entity):
    """Singleton entity that acts as a container for all device and app management functionality."""

    @odata(name="managedAppRegistrations")
    @property
    def managed_app_registrations(self):
        """"""
        return self.properties.get(
            "managedAppRegistrations",
            EntityCollection(
                self.context, ManagedAppRegistration, ResourcePath("managedAppRegistrations", self.resource_path)
            ),
        )

    @property
    def is_enabled_for_microsoft_store_for_business(self) -> Optional[bool]:
        """Gets the isEnabledForMicrosoftStoreForBusiness property"""
        return self.properties.get("isEnabledForMicrosoftStoreForBusiness", None)

    @property
    def microsoft_store_for_business_language(self) -> Optional[str]:
        """Gets the microsoftStoreForBusinessLanguage property"""
        return self.properties.get("microsoftStoreForBusinessLanguage", None)

    @property
    def microsoft_store_for_business_last_completed_application_sync_time(self) -> datetime:
        """Gets the microsoftStoreForBusinessLastCompletedApplicationSyncTime property"""
        return self.properties.get("microsoftStoreForBusinessLastCompletedApplicationSyncTime", datetime.min)

    @property
    def microsoft_store_for_business_last_successful_sync_date_time(self) -> datetime:
        """Gets the microsoftStoreForBusinessLastSuccessfulSyncDateTime property"""
        return self.properties.get("microsoftStoreForBusinessLastSuccessfulSyncDateTime", datetime.min)

    @property
    def managed_e_books(self) -> EntityCollection[ManagedEBook]:
        """Gets the managedEBooks property"""
        return self.properties.get(
            "managedEBooks",
            EntityCollection[ManagedEBook](
                self.context, ManagedEBook, ResourcePath("managedEBooks", self.resource_path)
            ),
        )

    @property
    def mobile_app_categories(self) -> EntityCollection[MobileAppCategory]:
        """Gets the mobileAppCategories property"""
        return self.properties.get(
            "mobileAppCategories",
            EntityCollection[MobileAppCategory](
                self.context, MobileAppCategory, ResourcePath("mobileAppCategories", self.resource_path)
            ),
        )

    @property
    def mobile_app_relationships(self) -> EntityCollection[MobileAppRelationship]:
        """Gets the mobileAppRelationships property"""
        return self.properties.get(
            "mobileAppRelationships",
            EntityCollection[MobileAppRelationship](
                self.context, MobileAppRelationship, ResourcePath("mobileAppRelationships", self.resource_path)
            ),
        )

    @property
    def mobile_apps(self) -> EntityCollection[MobileApp]:
        """Gets the mobileApps property"""
        return self.properties.get(
            "mobileApps",
            EntityCollection[MobileApp](self.context, MobileApp, ResourcePath("mobileApps", self.resource_path)),
        )

    @property
    def vpp_tokens(self) -> EntityCollection[VppToken]:
        """Gets the vppTokens property"""
        return self.properties.get(
            "vppTokens",
            EntityCollection[VppToken](self.context, VppToken, ResourcePath("vppTokens", self.resource_path)),
        )

    @property
    def managed_app_policies(self) -> EntityCollection[ManagedAppPolicy]:
        """Gets the managedAppPolicies property"""
        return self.properties.get(
            "managedAppPolicies",
            EntityCollection[ManagedAppPolicy](
                self.context, ManagedAppPolicy, ResourcePath("managedAppPolicies", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceAppManagement"

    @property
    def mobile_app_configurations(self) -> EntityCollection[ManagedDeviceMobileAppConfiguration]:
        """Gets the mobileAppConfigurations property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration import (
            ManagedDeviceMobileAppConfiguration,
        )

        return self.properties.get(
            "mobileAppConfigurations",
            EntityCollection[ManagedDeviceMobileAppConfiguration](
                self.context,
                ManagedDeviceMobileAppConfiguration,
                ResourcePath("mobileAppConfigurations", self.resource_path),
            ),
        )

    @property
    def android_managed_app_protections(self) -> EntityCollection[AndroidManagedAppProtection]:
        """Gets the androidManagedAppProtections property"""
        from office365.intune.devices.management.managed.app.protections.android import (
            AndroidManagedAppProtection,
        )

        return self.properties.get(
            "androidManagedAppProtections",
            EntityCollection[AndroidManagedAppProtection](
                self.context,
                AndroidManagedAppProtection,
                ResourcePath("androidManagedAppProtections", self.resource_path),
            ),
        )

    @property
    def default_managed_app_protections(self) -> EntityCollection[DefaultManagedAppProtection]:
        """Gets the defaultManagedAppProtections property"""
        from office365.intune.devices.management.managed.app.protections.default import (
            DefaultManagedAppProtection,
        )

        return self.properties.get(
            "defaultManagedAppProtections",
            EntityCollection[DefaultManagedAppProtection](
                self.context,
                DefaultManagedAppProtection,
                ResourcePath("defaultManagedAppProtections", self.resource_path),
            ),
        )

    @property
    def ios_managed_app_protections(self) -> EntityCollection[IosManagedAppProtection]:
        """Gets the iosManagedAppProtections property"""
        from office365.intune.devices.management.managed.app.protections.ios import (
            IosManagedAppProtection,
        )

        return self.properties.get(
            "iosManagedAppProtections",
            EntityCollection[IosManagedAppProtection](
                self.context, IosManagedAppProtection, ResourcePath("iosManagedAppProtections", self.resource_path)
            ),
        )

    @property
    def managed_app_statuses(self) -> EntityCollection[ManagedAppStatus]:
        """Gets the managedAppStatuses property"""
        from office365.intune.devices.management.managed.app.status import (
            ManagedAppStatus,
        )

        return self.properties.get(
            "managedAppStatuses",
            EntityCollection[ManagedAppStatus](
                self.context, ManagedAppStatus, ResourcePath("managedAppStatuses", self.resource_path)
            ),
        )

    @property
    def mdm_windows_information_protection_policies(self) -> EntityCollection[MdmWindowsInformationProtectionPolicy]:
        """Gets the mdmWindowsInformationProtectionPolicies property"""
        from office365.intune.devices.management.mdm_windows_information_protection_policy import (
            MdmWindowsInformationProtectionPolicy,
        )

        return self.properties.get(
            "mdmWindowsInformationProtectionPolicies",
            EntityCollection[MdmWindowsInformationProtectionPolicy](
                self.context,
                MdmWindowsInformationProtectionPolicy,
                ResourcePath("mdmWindowsInformationProtectionPolicies", self.resource_path),
            ),
        )

    @property
    def targeted_managed_app_configurations(self) -> EntityCollection[TargetedManagedAppConfiguration]:
        """Gets the targetedManagedAppConfigurations property"""
        from office365.intune.devices.management.targeted_managed_app_configuration import (
            TargetedManagedAppConfiguration,
        )

        return self.properties.get(
            "targetedManagedAppConfigurations",
            EntityCollection[TargetedManagedAppConfiguration](
                self.context,
                TargetedManagedAppConfiguration,
                ResourcePath("targetedManagedAppConfigurations", self.resource_path),
            ),
        )

    @property
    def windows_information_protection_policies(self) -> EntityCollection[WindowsInformationProtectionPolicy]:
        """Gets the windowsInformationProtectionPolicies property"""
        from office365.intune.devices.management.windows_information_protection_policy import (
            WindowsInformationProtectionPolicy,
        )

        return self.properties.get(
            "windowsInformationProtectionPolicies",
            EntityCollection[WindowsInformationProtectionPolicy](
                self.context,
                WindowsInformationProtectionPolicy,
                ResourcePath("windowsInformationProtectionPolicies", self.resource_path),
            ),
        )
