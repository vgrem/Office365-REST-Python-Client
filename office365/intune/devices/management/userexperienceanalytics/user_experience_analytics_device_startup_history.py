from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.operatingsystemrestartcategory import (
        UserExperienceAnalyticsOperatingSystemRestartCategory,
    )


class UserExperienceAnalyticsDeviceStartupHistory(Entity):
    @property
    def core_boot_time_in_ms(self) -> Optional[int]:
        """Gets the coreBootTimeInMs property"""
        return self.properties.get("coreBootTimeInMs", None)

    @property
    def core_login_time_in_ms(self) -> Optional[int]:
        """Gets the coreLoginTimeInMs property"""
        return self.properties.get("coreLoginTimeInMs", None)

    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def feature_update_boot_time_in_ms(self) -> Optional[int]:
        """Gets the featureUpdateBootTimeInMs property"""
        return self.properties.get("featureUpdateBootTimeInMs", None)

    @property
    def group_policy_boot_time_in_ms(self) -> Optional[int]:
        """Gets the groupPolicyBootTimeInMs property"""
        return self.properties.get("groupPolicyBootTimeInMs", None)

    @property
    def group_policy_login_time_in_ms(self) -> Optional[int]:
        """Gets the groupPolicyLoginTimeInMs property"""
        return self.properties.get("groupPolicyLoginTimeInMs", None)

    @property
    def is_feature_update(self) -> Optional[bool]:
        """Gets the isFeatureUpdate property"""
        return self.properties.get("isFeatureUpdate", None)

    @property
    def is_first_login(self) -> Optional[bool]:
        """Gets the isFirstLogin property"""
        return self.properties.get("isFirstLogin", None)

    @property
    def operating_system_version(self) -> Optional[str]:
        """Gets the operatingSystemVersion property"""
        return self.properties.get("operatingSystemVersion", None)

    @property
    def responsive_desktop_time_in_ms(self) -> Optional[int]:
        """Gets the responsiveDesktopTimeInMs property"""
        return self.properties.get("responsiveDesktopTimeInMs", None)

    @property
    def restart_category(self) -> UserExperienceAnalyticsOperatingSystemRestartCategory:
        """Gets the restartCategory property"""
        from office365.intune.devices.management.userexperienceanalytics.operatingsystemrestartcategory import (
            UserExperienceAnalyticsOperatingSystemRestartCategory,
        )

        return self.properties.get("restartCategory", UserExperienceAnalyticsOperatingSystemRestartCategory.unknown)

    @property
    def restart_fault_bucket(self) -> Optional[str]:
        """Gets the restartFaultBucket property"""
        return self.properties.get("restartFaultBucket", None)

    @property
    def restart_stop_code(self) -> Optional[str]:
        """Gets the restartStopCode property"""
        return self.properties.get("restartStopCode", None)

    @property
    def start_time(self) -> Optional[datetime]:
        """Gets the startTime property"""
        return self.properties.get("startTime", datetime.min)

    @property
    def total_boot_time_in_ms(self) -> Optional[int]:
        """Gets the totalBootTimeInMs property"""
        return self.properties.get("totalBootTimeInMs", None)

    @property
    def total_login_time_in_ms(self) -> Optional[int]:
        """Gets the totalLoginTimeInMs property"""
        return self.properties.get("totalLoginTimeInMs", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsDeviceStartupHistory"
