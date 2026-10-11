from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.conditions.conditions import (
        AuthenticationConditions,
    )


class AuthenticationEventsFlow(Entity):
    @property
    def conditions(self) -> AuthenticationConditions:
        """Gets the conditions property"""
        from office365.directory.authentication.conditions.conditions import (
            AuthenticationConditions,
        )

        return self.properties.get("conditions", AuthenticationConditions())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuthenticationEventsFlow"
