from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.identitygovernance.privilegedaccess.group import (
    PrivilegedAccessGroup,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.privilegedaccess.role_management_custom_callout_extension import (
        RoleManagementCustomCalloutExtension,
    )


class PrivilegedAccessRoot(Entity):
    """Represents the entry point for resources related to Privileged Identity Management (PIM)."""

    @property
    def group(self):
        """A list of pending user consent requests."""
        return self.properties.get(
            "group", PrivilegedAccessGroup(self.context, ResourcePath("group", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrivilegedAccessRoot"

    @property
    def custom_extensions(self) -> EntityCollection[RoleManagementCustomCalloutExtension]:
        """Gets the customExtensions property"""
        from office365.directory.identitygovernance.privilegedaccess.role_management_custom_callout_extension import (
            RoleManagementCustomCalloutExtension,
        )

        return self.properties.get(
            "customExtensions",
            EntityCollection[RoleManagementCustomCalloutExtension](
                self.context, RoleManagementCustomCalloutExtension, ResourcePath("customExtensions", self.resource_path)
            ),
        )
