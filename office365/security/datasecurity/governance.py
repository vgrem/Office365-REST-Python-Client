from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.datasecurity.sensitivity_label import SensitivityLabel

if TYPE_CHECKING:
    from office365.security.datasecurity.tenant_protection_scope_container import (
        TenantProtectionScopeContainer,
    )


class TenantDataSecurityAndGovernance(Entity):
    """Tenant-level container for data security and governance settings."""

    @odata(name="sensitivityLabels")
    @property
    def sensitivity_labels(self) -> EntityCollection[SensitivityLabel]:
        return self.properties.get(
            "sensitivityLabels",
            EntityCollection(self.context, SensitivityLabel, ResourcePath("sensitivityLabels", self.resource_path)),
        )

    @property
    def protection_scopes(self) -> TenantProtectionScopeContainer:
        """Gets the protectionScopes property"""
        from office365.security.datasecurity.tenant_protection_scope_container import (
            TenantProtectionScopeContainer,
        )

        return self.properties.get(
            "protectionScopes",
            TenantProtectionScopeContainer(self.context, ResourcePath("protectionScopes", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantDataSecurityAndGovernance"
