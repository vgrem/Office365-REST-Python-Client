from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.ios.ios_device_type import (
        IosDeviceType,
    )
    from office365.intune.devices.management.mobileapps.vpp_licensing_type import VppLicensingType
    from office365.intune.devices.management.vpptokens.accounttype import (
        VppTokenAccountType,
    )


class IosVppApp(Entity):
    @property
    def applicable_device_type(self) -> IosDeviceType:
        """Gets the applicableDeviceType property"""
        from office365.intune.devices.management.mobileapps.ios.ios_device_type import (
            IosDeviceType,
        )

        return self.properties.get("applicableDeviceType", IosDeviceType())

    @property
    def app_store_url(self) -> Optional[str]:
        """Gets the appStoreUrl property"""
        return self.properties.get("appStoreUrl", None)

    @property
    def bundle_id(self) -> Optional[str]:
        """Gets the bundleId property"""
        return self.properties.get("bundleId", None)

    @property
    def licensing_type(self) -> VppLicensingType:
        """Gets the licensingType property"""
        from office365.intune.devices.management.mobileapps.vpp_licensing_type import VppLicensingType

        return self.properties.get("licensingType", VppLicensingType())

    @property
    def release_date_time(self) -> Optional[datetime]:
        """Gets the releaseDateTime property"""
        return self.properties.get("releaseDateTime", datetime.min)

    @property
    def total_license_count(self) -> Optional[int]:
        """Gets the totalLicenseCount property"""
        return self.properties.get("totalLicenseCount", None)

    @property
    def used_license_count(self) -> Optional[int]:
        """Gets the usedLicenseCount property"""
        return self.properties.get("usedLicenseCount", None)

    @property
    def vpp_token_account_type(self) -> VppTokenAccountType:
        """Gets the vppTokenAccountType property"""
        from office365.intune.devices.management.vpptokens.accounttype import (
            VppTokenAccountType,
        )

        return self.properties.get("vppTokenAccountType", VppTokenAccountType.business)

    @property
    def vpp_token_apple_id(self) -> Optional[str]:
        """Gets the vppTokenAppleId property"""
        return self.properties.get("vppTokenAppleId", None)

    @property
    def vpp_token_organization_name(self) -> Optional[str]:
        """Gets the vppTokenOrganizationName property"""
        return self.properties.get("vppTokenOrganizationName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosVppApp"
