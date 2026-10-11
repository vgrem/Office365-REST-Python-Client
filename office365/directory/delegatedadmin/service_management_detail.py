from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DelegatedAdminServiceManagementDetail(Entity):
    @property
    def service_management_url(self) -> Optional[str]:
        """Gets the serviceManagementUrl property"""
        return self.properties.get("serviceManagementUrl", None)

    @property
    def service_name(self) -> Optional[str]:
        """Gets the serviceName property"""
        return self.properties.get("serviceName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminServiceManagementDetail"
