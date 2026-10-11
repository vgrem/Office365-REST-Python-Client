from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.applications.app_identity import AppIdentity
    from office365.intune.print.task import PrintTask


class PrintTaskDefinition(Entity):
    @property
    def created_by(self) -> AppIdentity:
        """Gets the createdBy property"""
        from office365.directory.applications.app_identity import AppIdentity

        return self.properties.get("createdBy", AppIdentity())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def tasks(self) -> EntityCollection[PrintTask]:
        """Gets the tasks property"""
        from office365.intune.print.task import PrintTask

        return self.properties.get(
            "tasks", EntityCollection[PrintTask](self.context, PrintTask, ResourcePath("tasks", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintTaskDefinition"
