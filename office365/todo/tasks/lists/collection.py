from office365.delta_collection import DeltaCollection
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.todo.tasks.lists.list import TodoTaskList


class TodoTaskListCollection(DeltaCollection[TodoTaskList]):
    """ """

    def __init__(self, context, resource_path=None):
        super().__init__(context, TodoTaskList, resource_path)

    def add(self, display_name: str) -> TodoTaskList:
        """Create a new lists object.

        Args:
            display_name (str): Field indicating title of the task list.
        """
        return super().add(displayName=display_name)

    def ensure(self, display_name: str) -> TodoTaskList:
        """Ensure a Task List with the given name exists (idempotent)."""
        return_type = TodoTaskList(self.context, EntityPath(None, self.resource_path))
        return_type.set_property("displayName", display_name)
        self.add_child(return_type)

        def _ensure(col: TodoTaskListCollection):
            if len(col) == 0:
                qry = CreateEntityQuery(self, return_type, return_type)
                self.context.add_query(qry)
            else:
                return_type.copy_from(col[0])

        self.get().filter(f"displayName eq '{display_name}'").after_execute(_ensure)
        return return_type
