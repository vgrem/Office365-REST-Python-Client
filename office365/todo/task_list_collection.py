from office365.entity_collection import EntityCollection
from office365.todo.task_list import TodoTaskList


class TodoTaskListCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(TodoTaskListCollection, self).__init__(context, TodoTaskList, resource_path)

    def add(self, display_name):
        """
        Create a new lists object.

        :param str display_name: Field indicating title of the task list.
        """
        return super(TodoTaskListCollection, self).add(displayName=display_name)
