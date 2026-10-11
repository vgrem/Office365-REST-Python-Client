from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.conditions.conditions import (
        AuthenticationConditions,
    )


class AuthenticationEventListener(Entity):
    """
    Defines a listener to evaluate when an authentication event happens in an authentication experience.
    An authenticationListener is abstract and is the base class of the various types of listeners you can evaluate
    during an authentication event.
    """

    @property
    def authentication_events_flow_id(self) -> Optional[str]:
        """Gets the authenticationEventsFlowId property"""
        return self.properties.get("authenticationEventsFlowId", None)

    @property
    def conditions(self) -> AuthenticationConditions:
        """Gets the conditions property"""
        from office365.directory.authentication.conditions.conditions import (
            AuthenticationConditions,
        )

        return self.properties.get("conditions", AuthenticationConditions())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuthenticationEventListener"
