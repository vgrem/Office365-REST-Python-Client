from __future__ import annotations

from typing import Optional

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class ThemeInfo(Entity):
    """Specifies a theme for a site"""

    def get_theme_font_by_name(self, name: str, lcid: int) -> ClientResult[str]:
        """Returns the name of the theme font for the specified font slot name and language code identifier (LCID).
        MUST return null if the font slot does not exist.

        Args:
            name (str): Name of the font slot.
            lcid (int): The language code identifier (LCID) for the required language.
        """
        return_type = ClientResult(self.context, str())
        payload = {"name": name, "lcid": lcid}
        qry = ServiceOperationQuery(self, "GetThemeFontByName", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def accessible_description(self) -> Optional[str]:
        """Specifies the accessible description for this theme."""
        return self.properties.get("AccessibleDescription", None)

    @property
    def theme_background_image_uri(self) -> Optional[str]:
        """Specifies the URI of the background image for this theme."""
        return self.properties.get("ThemeBackgroundImageUri", None)

    def get_theme_shade_by_name(self, name: str) -> ClientResult[str]:
        """GetThemeShadeByName operation.

        Args:
            name (str):
                name parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetThemeShadeByName", None, {"name": name}, None, return_type)
        self.context.add_query(qry)
        return return_type
