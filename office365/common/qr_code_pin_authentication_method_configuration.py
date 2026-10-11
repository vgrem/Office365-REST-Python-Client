from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.methods.target import (
        AuthenticationMethodTarget,
    )


class QrCodePinAuthenticationMethodConfiguration(Entity):
    @property
    def pin_length(self) -> Optional[int]:
        """Gets the pinLength property"""
        return self.properties.get("pinLength", None)

    @property
    def standard_qr_code_lifetime_in_days(self) -> Optional[int]:
        """Gets the standardQRCodeLifetimeInDays property"""
        return self.properties.get("standardQRCodeLifetimeInDays", None)

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
        return "microsoft.graph.QrCodePinAuthenticationMethodConfiguration"
