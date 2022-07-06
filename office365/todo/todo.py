from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.todo.task_list import TodoTaskList


class Todo(Entity):
    """Represents the To Do services available to a user."""

    @property
    def lists(self):
        """The task lists in the users mailbox."""
        return self.properties.get('lists',
                                   EntityCollection(self.context, TodoTaskList,
                                                    ResourcePath("lists", self.resource_path)))
