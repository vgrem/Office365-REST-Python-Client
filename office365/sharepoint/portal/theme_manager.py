from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.utilities.jsontheme import JsonTheme
from office365.sharepoint.utilities.themingoptions import ThemingOptions

if TYPE_CHECKING:
    from office365.sharepoint.portal.theme_manager import ThemeManager


class ThemeManager(Entity):
    """SharePoint site theming REST interface to perform basic create, read, update, and delete (CRUD)
    operations on site themes."""

    @property
    def entity_type_name(self):
        return "SP.Utilities.ThemeManager"

    def add_tenant_theme(self, name: str, theme_json: str) -> ClientResult[bool]:
        """Adds a new theme to a tenant.

        Args:
            name (str):
            theme_json (str):
        """
        return_type = ClientResult(self.context, bool())
        payload = {"name": name, "themeJson": theme_json}
        qry = ServiceOperationQuery(self, "AddTenantTheme", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_tenant_theme(self, name: str) -> Self:
        """
        Removes a theme.
        """
        payload = {"name": name}
        qry = ServiceOperationQuery(self, "DeleteTenantTheme", None, payload)
        self.context.add_query(qry)
        return self

    def add_tenant_theme_advanced(self, name: str, theme_json: str, should_parse_color_pair: bool) -> ClientResult[bool]:
        """AddTenantThemeAdvanced operation.

        Args:
            name (str): name parameter
            theme_json (str): themeJson parameter
            should_parse_color_pair (bool): shouldParseColorPair parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "AddTenantThemeAdvanced",
            None,
            {"name": name, "themeJson": theme_json, "shouldParseColorPair": should_parse_color_pair},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def apply_theme(self, name: str, theme_json: str) -> ClientResult[str]:
        """ApplyTheme operation.

        Args:
            name (str): name parameter
            theme_json (str): themeJson parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ApplyTheme", None, {"name": name, "themeJson": theme_json}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_available_themes(self) -> ClientResult[ClientValueCollection[JsonTheme]]:
        """GetAvailableThemes operation."""
        return_type = ClientResult(self.context, ClientValueCollection[JsonTheme]())
        qry = FunctionQuery(self, "GetAvailableThemes", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_hide_default_themes(self) -> ClientResult[bool]:
        """GetHideDefaultThemes operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "GetHideDefaultThemes", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_theme(self, name: str) -> ClientResult[JsonTheme]:
        """GetTenantTheme operation.

        Args:
            name (str): name parameter
        """
        return_type = ClientResult(self.context, JsonTheme())
        qry = FunctionQuery(self, "GetTenantTheme", [name], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_theming_options(self) -> ClientResult[ThemingOptions]:
        """GetTenantThemingOptions operation."""
        return_type = ClientResult(self.context, ThemingOptions())
        qry = FunctionQuery(self, "GetTenantThemingOptions", [], return_type)
        self.context.add_query(qry)
        return return_type

    def set_hide_default_themes(self, hide_default_themes: bool) -> ClientResult[bool]:
        """SetHideDefaultThemes operation.

        Args:
            hide_default_themes (bool): hideDefaultThemes parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "SetHideDefaultThemes", None, {"hideDefaultThemes": hide_default_themes}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def update_tenant_theme(self, name: str, theme_json: str) -> ClientResult[bool]:
        """UpdateTenantTheme operation.

        Args:
            name (str): name parameter
            theme_json (str): themeJson parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "UpdateTenantTheme", None, {"name": name, "themeJson": theme_json}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def update_tenant_theme_advanced(
        self, name: str, theme_json: str, should_parse_color_pair: bool
    ) -> ClientResult[bool]:
        """UpdateTenantThemeAdvanced operation.

        Args:
            name (str): name parameter
            theme_json (str): themeJson parameter
            should_parse_color_pair (bool): shouldParseColorPair parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "UpdateTenantThemeAdvanced",
            None,
            {"name": name, "themeJson": theme_json, "shouldParseColorPair": should_parse_color_pair},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    @property
    def context_theme_manager(self) -> ThemeManager:
        """Gets the ContextThemeManager property"""
        from office365.sharepoint.portal.theme_manager import ThemeManager

        return self.properties.get(
            "ContextThemeManager", ThemeManager(self.context, ResourcePath("ContextThemeManager", self.resource_path))
        )
