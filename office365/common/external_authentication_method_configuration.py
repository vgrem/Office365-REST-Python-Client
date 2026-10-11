from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.methods.target import (
        AuthenticationMethodTarget,
    )
    from office365.directory.authentication.open_id_connect_setting import (
        OpenIdConnectSetting,
    )


class ExternalAuthenticationMethodConfiguration(Entity):
    @property
    def app_id(self) -> Optional[str]:
        """Gets the appId property"""
        return self.properties.get("appId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def open_id_connect_setting(self) -> OpenIdConnectSetting:
        """Gets the openIdConnectSetting property"""
        from office365.directory.authentication.open_id_connect_setting import (
            OpenIdConnectSetting,
        )

        return self.properties.get("openIdConnectSetting", OpenIdConnectSetting())

    @property
    def include_targets(self) -> EntityCollection[AuthenticationMethodTarget]:
        """Gets the includeTargets property"""
        from office365.directory.authentication.methods.target import (
            AuthenticationMethodTarget,
        )

        return self.properties.get(
            "includeTargets",
            EntityCollection[AuthenticationMethodTarget](
                self.context, AuthenticationMethodTarget, ResourcePath("includeTargets", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExternalAuthenticationMethodConfiguration"
