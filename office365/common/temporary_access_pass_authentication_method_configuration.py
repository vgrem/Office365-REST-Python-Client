from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.methods.target import (
        AuthenticationMethodTarget,
    )


class TemporaryAccessPassAuthenticationMethodConfiguration(Entity):
    @property
    def default_length(self) -> Optional[int]:
        """Gets the defaultLength property"""
        return self.properties.get("defaultLength", None)

    @property
    def default_lifetime_in_minutes(self) -> Optional[int]:
        """Gets the defaultLifetimeInMinutes property"""
        return self.properties.get("defaultLifetimeInMinutes", None)

    @property
    def is_usable_once(self) -> Optional[bool]:
        """Gets the isUsableOnce property"""
        return self.properties.get("isUsableOnce", None)

    @property
    def maximum_lifetime_in_minutes(self) -> Optional[int]:
        """Gets the maximumLifetimeInMinutes property"""
        return self.properties.get("maximumLifetimeInMinutes", None)

    @property
    def minimum_lifetime_in_minutes(self) -> Optional[int]:
        """Gets the minimumLifetimeInMinutes property"""
        return self.properties.get("minimumLifetimeInMinutes", None)

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
        return "microsoft.graph.TemporaryAccessPassAuthenticationMethodConfiguration"
