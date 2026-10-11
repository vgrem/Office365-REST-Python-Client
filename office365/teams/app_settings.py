from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class TeamsAppSettings(Entity):
    @property
    def allow_user_requests_for_app_access(self) -> Optional[bool]:
        """Gets the allowUserRequestsForAppAccess property"""
        return self.properties.get("allowUserRequestsForAppAccess", None)

    @property
    def is_user_personal_scope_resource_specific_consent_enabled(self) -> Optional[bool]:
        """Gets the isUserPersonalScopeResourceSpecificConsentEnabled property"""
        return self.properties.get("isUserPersonalScopeResourceSpecificConsentEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamsAppSettings"
