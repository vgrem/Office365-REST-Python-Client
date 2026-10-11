from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.cloud_pc import CloudPC
    from office365.security.cloud_pc_audit_event import CloudPcAuditEvent
    from office365.security.cloud_pc_device_image import CloudPcDeviceImage
    from office365.security.cloud_pc_gallery_image import CloudPcGalleryImage
    from office365.security.cloud_pc_on_premises_connection import (
        CloudPcOnPremisesConnection,
    )
    from office365.security.cloud_pc_provisioning_policy import (
        CloudPcProvisioningPolicy,
    )
    from office365.security.cloud_pc_report import CloudPcReport
    from office365.security.cloud_pc_service_plan import CloudPcServicePlan
    from office365.security.cloud_pc_user_setting import CloudPcUserSetting


class VirtualEndpoint(Entity):
    """
    Use the Cloud PC API to provision and manage virtual desktops for employees in an organization,
    or along with the Intune API to manage physical and virtual endpoints.
    """

    @property
    def audit_events(self) -> EntityCollection[CloudPcAuditEvent]:
        """Gets the auditEvents property"""
        from office365.security.cloud_pc_audit_event import CloudPcAuditEvent

        return self.properties.get(
            "auditEvents",
            EntityCollection[CloudPcAuditEvent](
                self.context, CloudPcAuditEvent, ResourcePath("auditEvents", self.resource_path)
            ),
        )

    @property
    def cloud_pcs(self) -> EntityCollection[CloudPC]:
        """Gets the cloudPCs property"""
        from office365.intune.devices.cloud_pc import CloudPC

        return self.properties.get(
            "cloudPCs", EntityCollection[CloudPC](self.context, CloudPC, ResourcePath("cloudPCs", self.resource_path))
        )

    @property
    def device_images(self) -> EntityCollection[CloudPcDeviceImage]:
        """Gets the deviceImages property"""
        from office365.security.cloud_pc_device_image import (
            CloudPcDeviceImage,
        )

        return self.properties.get(
            "deviceImages",
            EntityCollection[CloudPcDeviceImage](
                self.context, CloudPcDeviceImage, ResourcePath("deviceImages", self.resource_path)
            ),
        )

    @property
    def gallery_images(self) -> EntityCollection[CloudPcGalleryImage]:
        """Gets the galleryImages property"""
        from office365.security.cloud_pc_gallery_image import (
            CloudPcGalleryImage,
        )

        return self.properties.get(
            "galleryImages",
            EntityCollection[CloudPcGalleryImage](
                self.context, CloudPcGalleryImage, ResourcePath("galleryImages", self.resource_path)
            ),
        )

    @property
    def on_premises_connections(self) -> EntityCollection[CloudPcOnPremisesConnection]:
        """Gets the onPremisesConnections property"""
        from office365.security.cloud_pc_on_premises_connection import (
            CloudPcOnPremisesConnection,
        )

        return self.properties.get(
            "onPremisesConnections",
            EntityCollection[CloudPcOnPremisesConnection](
                self.context, CloudPcOnPremisesConnection, ResourcePath("onPremisesConnections", self.resource_path)
            ),
        )

    @property
    def provisioning_policies(self) -> EntityCollection[CloudPcProvisioningPolicy]:
        """Gets the provisioningPolicies property"""
        from office365.security.cloud_pc_provisioning_policy import (
            CloudPcProvisioningPolicy,
        )

        return self.properties.get(
            "provisioningPolicies",
            EntityCollection[CloudPcProvisioningPolicy](
                self.context, CloudPcProvisioningPolicy, ResourcePath("provisioningPolicies", self.resource_path)
            ),
        )

    @property
    def report(self) -> CloudPcReport:
        """Gets the report property"""
        from office365.security.cloud_pc_report import CloudPcReport

        return self.properties.get("report", CloudPcReport(self.context, ResourcePath("report", self.resource_path)))

    @property
    def service_plans(self) -> EntityCollection[CloudPcServicePlan]:
        """Gets the servicePlans property"""
        from office365.security.cloud_pc_service_plan import (
            CloudPcServicePlan,
        )

        return self.properties.get(
            "servicePlans",
            EntityCollection[CloudPcServicePlan](
                self.context, CloudPcServicePlan, ResourcePath("servicePlans", self.resource_path)
            ),
        )

    @property
    def user_settings(self) -> EntityCollection[CloudPcUserSetting]:
        """Gets the userSettings property"""
        from office365.security.cloud_pc_user_setting import (
            CloudPcUserSetting,
        )

        return self.properties.get(
            "userSettings",
            EntityCollection[CloudPcUserSetting](
                self.context, CloudPcUserSetting, ResourcePath("userSettings", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEndpoint"
