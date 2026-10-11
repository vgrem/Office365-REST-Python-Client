from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.copilot.package_access_entity import PackageAccessEntity
    from office365.copilot.package_element_detail import PackageElementDetail


class CopilotPackageDetail(Entity):
    @property
    def acquire_users_and_groups(self) -> ClientValueCollection[PackageAccessEntity]:
        """Gets the acquireUsersAndGroups property"""
        from office365.copilot.package_access_entity import PackageAccessEntity

        return self.properties.get(
            "acquireUsersAndGroups", ClientValueCollection[PackageAccessEntity](PackageAccessEntity)
        )

    @property
    def active_users(self) -> Optional[int]:
        """Gets the activeUsers property"""
        return self.properties.get("activeUsers", None)

    @property
    def allowed_users_and_groups(self) -> ClientValueCollection[PackageAccessEntity]:
        """Gets the allowedUsersAndGroups property"""
        from office365.copilot.package_access_entity import PackageAccessEntity

        return self.properties.get(
            "allowedUsersAndGroups", ClientValueCollection[PackageAccessEntity](PackageAccessEntity)
        )

    @property
    def categories(self) -> StringCollection:
        """Gets the categories property"""
        return self.properties.get("categories", StringCollection())

    @property
    def element_details(self) -> ClientValueCollection[PackageElementDetail]:
        """Gets the elementDetails property"""
        from office365.copilot.package_element_detail import PackageElementDetail

        return self.properties.get("elementDetails", ClientValueCollection[PackageElementDetail](PackageElementDetail))

    @property
    def exception_rate(self) -> Optional[float]:
        """Gets the exceptionRate property"""
        return self.properties.get("exceptionRate", None)

    @property
    def last_used_date_time(self) -> Optional[datetime]:
        """Gets the lastUsedDateTime property"""
        return self.properties.get("lastUsedDateTime", datetime.min)

    @property
    def long_description(self) -> Optional[str]:
        """Gets the longDescription property"""
        return self.properties.get("longDescription", None)

    @property
    def sensitivity(self) -> Optional[str]:
        """Gets the sensitivity property"""
        return self.properties.get("sensitivity", None)

    @property
    def shared_with_users_and_groups(self) -> ClientValueCollection[PackageAccessEntity]:
        """Gets the sharedWithUsersAndGroups property"""
        from office365.copilot.package_access_entity import PackageAccessEntity

        return self.properties.get(
            "sharedWithUsersAndGroups", ClientValueCollection[PackageAccessEntity](PackageAccessEntity)
        )

    @property
    def total_run_time_in_hours(self) -> Optional[float]:
        """Gets the totalRunTimeInHours property"""
        return self.properties.get("totalRunTimeInHours", None)

    @property
    def total_sessions(self) -> Optional[int]:
        """Gets the totalSessions property"""
        return self.properties.get("totalSessions", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotPackageDetail"
