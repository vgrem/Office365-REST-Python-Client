from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.directory.tenant_service_info_value import (
        TenantServiceInfoValue,
    )


class Tenant(Entity):
    @property
    def id(self) -> Optional[UUID]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def entity_type_name(self) -> str:
        return "SP.Directory.Tenant"

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def service_info(self) -> ClientValueCollection[TenantServiceInfoValue]:
        """Gets the serviceInfo property"""
        from office365.sharepoint.directory.tenant_service_info_value import (
            TenantServiceInfoValue,
        )

        return self.properties.get("serviceInfo", ClientValueCollection[TenantServiceInfoValue](TenantServiceInfoValue))
