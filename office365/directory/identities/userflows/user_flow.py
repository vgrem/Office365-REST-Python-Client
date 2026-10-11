from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.userflows.userflowtype import UserFlowType


class IdentityUserFlow(Entity):
    @property
    def user_flow_type(self) -> UserFlowType:
        """Gets the userFlowType property"""
        from office365.directory.identities.userflows.userflowtype import UserFlowType

        return self.properties.get("userFlowType", UserFlowType.signUp)

    @property
    def user_flow_type_version(self) -> Optional[float]:
        """Gets the userFlowTypeVersion property"""
        return self.properties.get("userFlowTypeVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentityUserFlow"
