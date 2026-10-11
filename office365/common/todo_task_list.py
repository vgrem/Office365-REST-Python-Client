from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.todo_task import TodoTask
    from office365.directory.extensions.extension import Extension
    from office365.onedrive.wellknown_list_name import WellknownListName


class TodoTaskList(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_owner(self) -> Optional[bool]:
        """Gets the isOwner property"""
        return self.properties.get("isOwner", None)

    @property
    def is_shared(self) -> Optional[bool]:
        """Gets the isShared property"""
        return self.properties.get("isShared", None)

    @property
    def wellknown_list_name(self) -> WellknownListName:
        """Gets the wellknownListName property"""
        from office365.onedrive.wellknown_list_name import WellknownListName

        return self.properties.get("wellknownListName", WellknownListName.none)

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """Gets the extensions property"""
        from office365.directory.extensions.extension import Extension

        return self.properties.get(
            "extensions",
            EntityCollection[Extension](self.context, Extension, ResourcePath("extensions", self.resource_path)),
        )

    @property
    def tasks(self) -> EntityCollection[TodoTask]:
        """Gets the tasks property"""
        from office365.common.todo_task import TodoTask

        return self.properties.get(
            "tasks", EntityCollection[TodoTask](self.context, TodoTask, ResourcePath("tasks", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TodoTaskList"
