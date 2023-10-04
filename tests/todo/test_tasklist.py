from office365.todo.tasks.list import TodoTaskList
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestTaskList(GraphTestCase):
    task_list = None  # type: TodoTaskList

    def test1_create_task_list(self):
        name = create_unique_name("TaskList")
        task_list = self.client.me.todo.lists.add(name).execute_query()
        self.__class__.task_list = task_list

    def test2_get_task_lists(self):
        task_lists = self.client.me.todo.lists.get().execute_query()
        self.assertIsNotNone(task_lists.resource_path)

    def test3_create_task(self):
        task = self.__class__.task_list.tasks.add(title="A new task").execute_query()
        self.assertIsNotNone(task.resource_path)

    def test4_list_tasks(self):
        tasks = self.__class__.task_list.tasks.get().execute_query()
        self.assertIsNotNone(tasks.resource_path)
        self.assertGreater(len(tasks), 0)

    def test5_delete_task_list(self):
        list_to_del = self.__class__.task_list
        list_to_del.delete_object().execute_query()
