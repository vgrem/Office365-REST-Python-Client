from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.copilot.copilot_package_request_status import (
        CopilotPackageRequestStatus,
    )
    from office365.copilot.copilot_package_request_type import CopilotPackageRequestType
    from office365.copilot.package_type import PackageType
    from office365.intune.devices.management.package_status import PackageStatus
    from office365.runtime.types.json import Json


class CopilotPackage(Entity):
    @property
    def agent_identity_id(self) -> Optional[str]:
        """Gets the agentIdentityId property"""
        return self.properties.get("agentIdentityId", None)

    @property
    def app_id(self) -> Optional[str]:
        """Gets the appId property"""
        return self.properties.get("appId", None)

    @property
    def asset_id(self) -> Optional[str]:
        """Gets the assetId property"""
        return self.properties.get("assetId", None)

    @property
    def available_to(self) -> PackageStatus:
        """Gets the availableTo property"""
        from office365.intune.devices.management.package_status import PackageStatus

        return self.properties.get("availableTo", PackageStatus.none)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def deployed_to(self) -> PackageStatus:
        """Gets the deployedTo property"""
        from office365.intune.devices.management.package_status import PackageStatus

        return self.properties.get("deployedTo", PackageStatus.none)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def element_types(self) -> StringCollection:
        """Gets the elementTypes property"""
        return self.properties.get("elementTypes", StringCollection())

    @property
    def governance_metadata(self) -> Json:
        """Gets the governanceMetadata property"""
        from office365.runtime.types.json import Json

        return self.properties.get("governanceMetadata", Json())

    @property
    def is_blocked(self) -> Optional[bool]:
        """Gets the isBlocked property"""
        return self.properties.get("isBlocked", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def manifest_id(self) -> Optional[str]:
        """Gets the manifestId property"""
        return self.properties.get("manifestId", None)

    @property
    def manifest_version(self) -> Optional[str]:
        """Gets the manifestVersion property"""
        return self.properties.get("manifestVersion", None)

    @property
    def owner_id(self) -> Optional[str]:
        """Gets the ownerId property"""
        return self.properties.get("ownerId", None)

    @property
    def platform(self) -> Optional[str]:
        """Gets the platform property"""
        return self.properties.get("platform", None)

    @property
    def publisher(self) -> Optional[str]:
        """Gets the publisher property"""
        return self.properties.get("publisher", None)

    @property
    def request_status(self) -> CopilotPackageRequestStatus:
        """Gets the requestStatus property"""
        from office365.copilot.copilot_package_request_status import (
            CopilotPackageRequestStatus,
        )

        return self.properties.get("requestStatus", CopilotPackageRequestStatus.pending)

    @property
    def request_type(self) -> CopilotPackageRequestType:
        """Gets the requestType property"""
        from office365.copilot.copilot_package_request_type import (
            CopilotPackageRequestType,
        )

        return self.properties.get("requestType", CopilotPackageRequestType.publish)

    @property
    def short_description(self) -> Optional[str]:
        """Gets the shortDescription property"""
        return self.properties.get("shortDescription", None)

    @property
    def supported_hosts(self) -> StringCollection:
        """Gets the supportedHosts property"""
        return self.properties.get("supportedHosts", StringCollection())

    @property
    def type(self) -> PackageType:
        """Gets the type property"""
        from office365.copilot.package_type import PackageType

        return self.properties.get("type", PackageType.microsoft)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def zip_file(self) -> Optional[bytes]:
        """Gets the zipFile property"""
        return self.properties.get("zipFile", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotPackage"
