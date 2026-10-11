from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.devices.management.managed.app.flaggedreason import (
    ManagedAppFlaggedReason,
)
from office365.intune.policies.managed_app import ManagedAppPolicy
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.app.operation import ManagedAppOperation
    from office365.intune.devices.management.mobileapps.mobile_app_identifier import MobileAppIdentifier


class ManagedAppRegistration(Entity):
    """
    The ManagedAppEntity is the base entity type for all other entity types under app management workflow.
    The ManagedAppRegistration resource represents the details of an app, with management capability,
    used by a member of the organization.
    """

    @property
    def application_version(self) -> Optional[str]:
        """Gets the applicationVersion property"""
        return self.properties.get("applicationVersion", None)

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the deviceName property"""
        return self.properties.get("deviceName", None)

    @property
    def device_tag(self) -> Optional[str]:
        """Gets the deviceTag property"""
        return self.properties.get("deviceTag", None)

    @property
    def device_type(self) -> Optional[str]:
        """Gets the deviceType property"""
        return self.properties.get("deviceType", None)

    @property
    def flagged_reasons(self) -> ClientValueCollection[ManagedAppFlaggedReason]:
        """Gets the flaggedReasons property"""
        return self.properties.get(
            "flaggedReasons", ClientValueCollection[ManagedAppFlaggedReason](ManagedAppFlaggedReason)
        )

    @property
    def last_sync_date_time(self) -> datetime:
        """Gets the lastSyncDateTime property"""
        return self.properties.get("lastSyncDateTime", datetime.min)

    @property
    def management_sdk_version(self) -> Optional[str]:
        """Gets the managementSdkVersion property"""
        return self.properties.get("managementSdkVersion", None)

    @property
    def platform_version(self) -> Optional[str]:
        """Gets the platformVersion property"""
        return self.properties.get("platformVersion", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def applied_policies(self) -> EntityCollection[ManagedAppPolicy]:
        """Gets the appliedPolicies property"""
        return self.properties.get(
            "appliedPolicies",
            EntityCollection[ManagedAppPolicy](
                self.context, ManagedAppPolicy, ResourcePath("appliedPolicies", self.resource_path)
            ),
        )

    @property
    def intended_policies(self) -> EntityCollection[ManagedAppPolicy]:
        """Gets the intendedPolicies property"""
        return self.properties.get(
            "intendedPolicies",
            EntityCollection[ManagedAppPolicy](
                self.context, ManagedAppPolicy, ResourcePath("intendedPolicies", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedAppRegistration"

    @property
    def app_identifier(self) -> MobileAppIdentifier:
        """Gets the appIdentifier property"""
        from office365.intune.devices.management.mobileapps.mobile_app_identifier import MobileAppIdentifier

        return self.properties.get("appIdentifier", MobileAppIdentifier())

    @property
    def operations(self) -> EntityCollection[ManagedAppOperation]:
        """Gets the operations property"""
        from office365.intune.devices.management.managed.app.operation import ManagedAppOperation

        return self.properties.get(
            "operations",
            EntityCollection[ManagedAppOperation](
                self.context, ManagedAppOperation, ResourcePath("operations", self.resource_path)
            ),
        )
