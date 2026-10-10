from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.brandcenter.configuration import BrandCenterConfiguration
from office365.sharepoint.brandcenter.theme_data import ThemeData
from office365.sharepoint.entity import Entity
from office365.sharepoint.sites.themes import SiteThemes

if TYPE_CHECKING:
    from office365.sharepoint.administration.orgassets.org_assets import OrgAssets
    from office365.sharepoint.brandcenter.tenantthemes import TenantThemes


class BrandCenter(Entity):
    """
    The SharePoint brand center API offers a centralized branding management application
    that empowers your brand managers or designated brand owners to help your organization to customize
    the look and feel of their experiences.
    """

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.BrandCenter"))

    def configuration(self) -> ClientResult[BrandCenterConfiguration]:
        """ """
        return_type = ClientResult(self.context, BrandCenterConfiguration())
        qry = ServiceOperationQuery(self, "Configuration", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_site_theme(self, theme_data: ThemeData) -> ClientResult[ThemeData]:
        """ """
        return_type = ClientResult(self.context, ThemeData())
        payload = {"themeData": theme_data}
        qry = ServiceOperationQuery(self, "AddSiteTheme", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_themes(self) -> ClientResult[SiteThemes]:
        """ """
        return_type = ClientResult(self.context, SiteThemes())
        qry = ServiceOperationQuery(self, "GetSiteThemes", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_tenant_theme(self, theme_data: ThemeData) -> ClientResult[ThemeData]:
        """AddTenantTheme operation.

        Args:
            theme_data (ThemeData):
                themeData parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = ServiceOperationQuery(self, "AddTenantTheme", None, {"themeData": theme_data}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def current_branding_configuration(self) -> ClientResult[BrandCenterConfiguration]:
        """CurrentBrandingConfiguration operation."""
        from office365.sharepoint.brandcenter.configuration import (
            BrandCenterConfiguration,
        )

        return_type = ClientResult(self.context, BrandCenterConfiguration())
        qry = FunctionQuery(self, "CurrentBrandingConfiguration", [], return_type)
        self.context.add_query(qry)
        return return_type

    def delete_site_theme(self, theme_id: int) -> Self:
        """DeleteSiteTheme operation.

        Args:
            theme_id (int):
                themeId parameter
        """
        qry = ServiceOperationQuery(self, "DeleteSiteTheme", None, {"themeId": theme_id}, None, None)
        self.context.add_query(qry)
        return self

    def delete_tenant_theme(self, theme_id: int) -> Self:
        """DeleteTenantTheme operation.

        Args:
            theme_id (int):
                themeId parameter
        """
        qry = ServiceOperationQuery(self, "DeleteTenantTheme", None, {"themeId": theme_id}, None, None)
        self.context.add_query(qry)
        return self

    def enable_brand_center_public_cdn(self) -> Self:
        """EnableBrandCenterPublicCdn operation."""
        qry = ServiceOperationQuery(self, "EnableBrandCenterPublicCdn", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def ensure_brand_colors_list_feature(self) -> ClientResult[OrgAssets]:
        """EnsureBrandColorsListFeature operation."""
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = ServiceOperationQuery(self, "EnsureBrandColorsListFeature", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def ensure_brand_fonts_library_feature(self) -> ClientResult[OrgAssets]:
        """EnsureBrandFontsLibraryFeature operation."""
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = ServiceOperationQuery(self, "EnsureBrandFontsLibraryFeature", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def ensure_org_skills_library(self) -> ClientResult[OrgAssets]:
        """EnsureOrgSkillsLibrary operation."""
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = ServiceOperationQuery(self, "EnsureOrgSkillsLibrary", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_font_stream(self, font_file_url: str) -> ClientResult[bytes]:
        """GetFontStream operation.

        Args:
            font_file_url (str):
                fontFileUrl parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "GetFontStream", [font_file_url], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def get_site_theme_by_id(self, id_: int) -> ClientResult[ThemeData]:
        """GetSiteThemeById operation.

        Args:
            id_ (int):
                id parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = FunctionQuery(self, "GetSiteThemeById", [id_], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_theme_by_id(self, id_: int) -> ClientResult[ThemeData]:
        """GetTenantThemeById operation.

        Args:
            id_ (int):
                id parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = FunctionQuery(self, "GetTenantThemeById", [id_], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_theme_by_name(self, name: str) -> ClientResult[ThemeData]:
        """GetTenantThemeByName operation.

        Args:
            name (str):
                name parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = FunctionQuery(self, "GetTenantThemeByName", [name], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_theme_by_name_xgeo_util(self, name: str) -> ClientResult[ThemeData]:
        """GetTenantThemeByNameXgeoUtil operation.

        Args:
            name (str):
                name parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = ServiceOperationQuery(self, "GetTenantThemeByNameXgeoUtil", None, {"name": name}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_themes(self) -> ClientResult[TenantThemes]:
        """GetTenantThemes operation."""
        from office365.sharepoint.brandcenter.tenantthemes import TenantThemes

        return_type = ClientResult(self.context, TenantThemes())
        qry = FunctionQuery(self, "GetTenantThemes", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_themes_xgeo_util(self) -> ClientResult[TenantThemes]:
        """GetTenantThemesXgeoUtil operation."""
        from office365.sharepoint.brandcenter.tenantthemes import TenantThemes

        return_type = ClientResult(self.context, TenantThemes())
        qry = ServiceOperationQuery(self, "GetTenantThemesXgeoUtil", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def org_assets(self) -> ClientResult[OrgAssets]:
        """OrgAssets operation."""
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = FunctionQuery(self, "OrgAssets", [], return_type)
        self.context.add_query(qry)
        return return_type

    def org_assets_with_cache_flag(self, should_use_cache: bool) -> ClientResult[OrgAssets]:
        """OrgAssetsWithCacheFlag operation.

        Args:
            should_use_cache (bool):
                shouldUseCache parameter
        """
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = FunctionQuery(self, "OrgAssetsWithCacheFlag", [should_use_cache], return_type)
        self.context.add_query(qry)
        return return_type

    def remove_brand_font_file_local(self, file_name: str) -> Self:
        """RemoveBrandFontFileLocal operation.

        Args:
            file_name (str):
                fileName parameter
        """
        qry = ServiceOperationQuery(self, "RemoveBrandFontFileLocal", None, {"fileName": file_name}, None, None)
        self.context.add_query(qry)
        return self

    def set_web_theme(self, name: str, web_url: str) -> ClientResult[str]:
        """SetWebTheme operation.

        Args:
            name (str):
                name parameter
            web_url (str):
                webUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "SetWebTheme", [name, web_url], return_type)
        self.context.add_query(qry)
        return return_type

    def update_site_theme(self, theme_data: ThemeData) -> ClientResult[ThemeData]:
        """UpdateSiteTheme operation.

        Args:
            theme_data (ThemeData):
                themeData parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = ServiceOperationQuery(self, "UpdateSiteTheme", None, {"themeData": theme_data}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def update_tenant_theme(self, theme_data: ThemeData) -> ClientResult[ThemeData]:
        """UpdateTenantTheme operation.

        Args:
            theme_data (ThemeData):
                themeData parameter
        """
        from office365.sharepoint.brandcenter.theme_data import ThemeData

        return_type = ClientResult(self.context, ThemeData())
        qry = ServiceOperationQuery(self, "UpdateTenantTheme", None, {"themeData": theme_data}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def validate_site_theme_name(self, name: str) -> ClientResult[bool]:
        """ValidateSiteThemeName operation.

        Args:
            name (str):
                name parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "ValidateSiteThemeName", None, {"name": name}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def validate_tenant_theme_name(self, name: str) -> ClientResult[bool]:
        """ValidateTenantThemeName operation.

        Args:
            name (str):
                name parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "ValidateTenantThemeName", None, {"name": name}, None, return_type)
        self.context.add_query(qry)
        return return_type
