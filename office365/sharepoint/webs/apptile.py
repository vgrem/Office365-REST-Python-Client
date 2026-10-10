from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class AppTile(Entity):
    @property
    def app_id(self) -> Optional[UUID]:
        """Gets the AppId property"""
        return self.properties.get("AppId", None)

    @property
    def app_principal_id(self) -> Optional[str]:
        """Gets the AppPrincipalId property"""
        return self.properties.get("AppPrincipalId", None)

    @property
    def app_source(self) -> Optional[int]:
        """Gets the AppSource property"""
        return self.properties.get("AppSource", None)

    @property
    def app_status(self) -> Optional[int]:
        """Gets the AppStatus property"""
        return self.properties.get("AppStatus", None)

    @property
    def app_type(self) -> Optional[int]:
        """Gets the AppType property"""
        return self.properties.get("AppType", None)

    @property
    def asset_id(self) -> Optional[str]:
        """Gets the AssetId property"""
        return self.properties.get("AssetId", None)

    @property
    def base_template(self) -> Optional[int]:
        """Gets the BaseTemplate property"""
        return self.properties.get("BaseTemplate", None)

    @property
    def child_count(self) -> Optional[int]:
        """Gets the ChildCount property"""
        return self.properties.get("ChildCount", None)

    @property
    def content_market(self) -> Optional[str]:
        """Gets the ContentMarket property"""
        return self.properties.get("ContentMarket", None)

    @property
    def custom_settings_url(self) -> Optional[str]:
        """Gets the CustomSettingsUrl property"""
        return self.properties.get("CustomSettingsUrl", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def is_corporate_catalog_site(self) -> Optional[bool]:
        """Gets the IsCorporateCatalogSite property"""
        return self.properties.get("IsCorporateCatalogSite", None)

    @property
    def last_modified(self) -> Optional[str]:
        """Gets the LastModified property"""
        return self.properties.get("LastModified", None)

    @property
    def last_modified_date(self) -> Optional[datetime]:
        """Gets the LastModifiedDate property"""
        return self.properties.get("LastModifiedDate", None)

    @property
    def product_id(self) -> Optional[UUID]:
        """Gets the ProductId property"""
        return self.properties.get("ProductId", None)

    @property
    def target(self) -> Optional[str]:
        """Gets the Target property"""
        return self.properties.get("Target", None)

    @property
    def thumbnail(self) -> Optional[str]:
        """Gets the Thumbnail property"""
        return self.properties.get("Thumbnail", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the Version property"""
        return self.properties.get("Version", None)

    @property
    def version_count(self) -> Optional[int]:
        """Gets the VersionCount property"""
        return self.properties.get("VersionCount", None)

    @property
    def version_size(self) -> Optional[int]:
        """Gets the VersionSize property"""
        return self.properties.get("VersionSize", None)
