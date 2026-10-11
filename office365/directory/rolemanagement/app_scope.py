from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AppScope(Entity):
    """
    The scope of a role assignment determines the set of resources for which the principal has been granted access.
    An app scope is a scope defined and understood by a specific application, unlike directory scopes that are
    shared scopes stored in the directory and understood by multiple applications.

    This may be in both the following principal and scope scenarios:

    A single principal and a single scope
    Multiple principals and multiple scopes.
    """

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def type(self) -> Optional[str]:
        """Gets the type property"""
        return self.properties.get("type", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AppScope"
