from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.devices.management.managed.app.dataencryptiontype import (
    ManagedAppDataEncryptionType,
)
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.app_policy_deployment_summary import (
        ManagedAppPolicyDeploymentSummary,
    )
    from office365.intune.devices.management.managed.mobile_app import ManagedMobileApp


class IosManagedAppProtection(Entity):
    @property
    def app_data_encryption_type(self) -> ManagedAppDataEncryptionType:
        """Gets the appDataEncryptionType property"""
        return self.properties.get("appDataEncryptionType", ManagedAppDataEncryptionType.useDeviceSettings)

    @property
    def custom_browser_protocol(self) -> Optional[str]:
        """Gets the customBrowserProtocol property"""
        return self.properties.get("customBrowserProtocol", None)

    @property
    def deployed_app_count(self) -> Optional[int]:
        """Gets the deployedAppCount property"""
        return self.properties.get("deployedAppCount", None)

    @property
    def face_id_blocked(self) -> Optional[bool]:
        """Gets the faceIdBlocked property"""
        return self.properties.get("faceIdBlocked", None)

    @property
    def minimum_required_sdk_version(self) -> Optional[str]:
        """Gets the minimumRequiredSdkVersion property"""
        return self.properties.get("minimumRequiredSdkVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosManagedAppProtection"

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
