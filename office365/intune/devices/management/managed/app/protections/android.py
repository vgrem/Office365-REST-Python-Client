from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.app_policy_deployment_summary import (
        ManagedAppPolicyDeploymentSummary,
    )
    from office365.intune.devices.management.managed.mobile_app import ManagedMobileApp


class AndroidManagedAppProtection(Entity):
    @property
    def custom_browser_display_name(self) -> Optional[str]:
        """Gets the customBrowserDisplayName property"""
        return self.properties.get("customBrowserDisplayName", None)

    @property
    def custom_browser_package_id(self) -> Optional[str]:
        """Gets the customBrowserPackageId property"""
        return self.properties.get("customBrowserPackageId", None)

    @property
    def deployed_app_count(self) -> Optional[int]:
        """Gets the deployedAppCount property"""
        return self.properties.get("deployedAppCount", None)

    @property
    def disable_app_encryption_if_device_encryption_is_enabled(self) -> Optional[bool]:
        """Gets the disableAppEncryptionIfDeviceEncryptionIsEnabled property"""
        return self.properties.get("disableAppEncryptionIfDeviceEncryptionIsEnabled", None)

    @property
    def encrypt_app_data(self) -> Optional[bool]:
        """Gets the encryptAppData property"""
        return self.properties.get("encryptAppData", None)

    @property
    def minimum_required_patch_version(self) -> Optional[str]:
        """Gets the minimumRequiredPatchVersion property"""
        return self.properties.get("minimumRequiredPatchVersion", None)

    @property
    def minimum_warning_patch_version(self) -> Optional[str]:
        """Gets the minimumWarningPatchVersion property"""
        return self.properties.get("minimumWarningPatchVersion", None)

    @property
    def screen_capture_blocked(self) -> Optional[bool]:
        """Gets the screenCaptureBlocked property"""
        return self.properties.get("screenCaptureBlocked", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AndroidManagedAppProtection"

    @property
    def apps(self) -> EntityCollection[ManagedMobileApp]:
        """Gets the apps property"""
        from office365.intune.devices.management.managed.mobile_app import ManagedMobileApp

        return self.properties.get(
            "apps",
            EntityCollection[ManagedMobileApp](self.context, ManagedMobileApp, ResourcePath("apps", self.resource_path)),
        )

    @property
    def deployment_summary(self) -> ManagedAppPolicyDeploymentSummary:
        """Gets the deploymentSummary property"""
        from office365.intune.devices.management.managed.app_policy_deployment_summary import (
            ManagedAppPolicyDeploymentSummary,
        )

        return self.properties.get(
            "deploymentSummary",
            ManagedAppPolicyDeploymentSummary(self.context, ResourcePath("deploymentSummary", self.resource_path)),
        )
