from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UnifiedRbacResourceAction(Entity):
    @property
    def action_verb(self) -> Optional[str]:
        """Gets the actionVerb property"""
        return self.properties.get("actionVerb", None)

    @property
    def authentication_context_id(self) -> Optional[str]:
        """Gets the authenticationContextId property"""
        return self.properties.get("authenticationContextId", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def is_authentication_context_settable(self) -> Optional[bool]:
        """Gets the isAuthenticationContextSettable property"""
        return self.properties.get("isAuthenticationContextSettable", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def resource_scope_id(self) -> Optional[str]:
        """Gets the resourceScopeId property"""
        return self.properties.get("resourceScopeId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRbacResourceAction"
