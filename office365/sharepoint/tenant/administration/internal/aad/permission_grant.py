from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SPO3rdPartyAADPermissionGrant(Entity):
    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.Internal.SPO3rdPartyAADPermissionGrant"

    @property
    def client_id(self) -> Optional[str]:
        """Gets the ClientId property"""
        return self.properties.get("ClientId", None)

    @property
    def consent_type(self) -> Optional[str]:
        """Gets the ConsentType property"""
        return self.properties.get("ConsentType", None)

    @property
    def is_domain_isolated(self) -> Optional[bool]:
        """Gets the IsDomainIsolated property"""
        return self.properties.get("IsDomainIsolated", None)

    @property
    def object_id(self) -> Optional[str]:
        """Gets the ObjectId property"""
        return self.properties.get("ObjectId", None)

    @property
    def package_name(self) -> Optional[str]:
        """Gets the PackageName property"""
        return self.properties.get("PackageName", None)

    @property
    def resource(self) -> Optional[str]:
        """Gets the Resource property"""
        return self.properties.get("Resource", None)

    @property
    def scope(self) -> Optional[str]:
        """Gets the Scope property"""
        return self.properties.get("Scope", None)
