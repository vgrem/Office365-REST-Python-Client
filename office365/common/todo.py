from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.todo_task_list import TodoTaskList


class Todo(Entity):
    @property
    def lists(self) -> EntityCollection[TodoTaskList]:
        """Gets the lists property"""
        from office365.common.todo_task_list import TodoTaskList

        return self.properties.get(
            "lists",
            EntityCollection[TodoTaskList](self.context, TodoTaskList, ResourcePath("lists", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Todo"
