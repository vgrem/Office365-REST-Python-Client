"""Microsoft To Do — task lists, tasks, checklist items, and linked resources.

Tests cover:
  - Creating a task list with a unique name
  - Listing all task lists
  - Creating a task in a list
  - Listing tasks in a list
  - Updating a task (title, status)
  - Getting a task by ID
  - Adding a checklist item (subtask)
  - Listing linked resources on a task
  - Deleting a task
  - Deleting a task list
  - Task and list property assertions
"""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.todo.tasks.lists.list import TodoTaskList
from office365.todo.tasks.task import TodoTask
from office365.todo.tasks.taskstatus import TaskStatus
from tests import create_unique_name
from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase


class TestTaskList(GraphDelegatedTestCase):
    """To Do task list and task lifecycle."""

    task_list: ClassVar[Optional[TodoTaskList]] = None
    task: ClassVar[Optional[TodoTask]] = None

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_01_create_task_list(self):
        """Creating a task list with a unique name should succeed."""
        name = create_unique_name("SDK Test TaskList")
        task_list = self.client.me.todo.lists.add(name).execute_query()
        self.assertIsNotNone(task_list.resource_path)
        self.assertEqual(task_list.display_name, name)
        TestTaskList.task_list = task_list

    @requires_delegated(
        "Tasks.Read",
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_02_list_task_lists(self):
        """Listing all task lists returns a valid collection."""
        lists = self.client.me.todo.lists.get().execute_query()
        self.assertIsNotNone(lists.resource_path)

    @requires_delegated(
        "Tasks.Read",
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_03_task_list_has_expected_properties(self):
        """A task list exposes displayName and wellknownListName."""
        tl = TestTaskList.task_list
        if not tl:
            self.skipTest("No task list created from previous test")

        self.assertIsNotNone(tl.display_name)
        self.assertIsNotNone(tl.get_property("wellknownListName"))

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_04_create_task(self):
        """Creating a task in the task list should succeed."""
        tl = TestTaskList.task_list
        if not tl:
            self.skipTest("No task list created from previous test")

        task = tl.tasks.add(title="SDK Test Task").execute_query()
        self.assertIsNotNone(task.resource_path)
        self.assertEqual(task.title, "SDK Test Task")
        TestTaskList.task = task

    @requires_delegated(
        "Tasks.Read",
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_05_list_tasks(self):
        """Listing tasks in the task list returns at least one task."""
        tl = TestTaskList.task_list
        if not tl:
            self.skipTest("No task list created from previous test")

        tasks = tl.tasks.get().execute_query()
        self.assertIsNotNone(tasks.resource_path)
        self.assertGreater(len(tasks), 0)

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_06_update_task_title_and_status(self):
        """Updating a task's title and marking it complete should persist."""
        task = TestTaskList.task
        if not task:
            self.skipTest("No task created from previous test")

        task.title = "SDK Updated Task Title"
        task.status = TaskStatus.completed
        task.update().execute_query()
        self.assertEqual(task.title, "SDK Updated Task Title")
        self.assertEqual(task.status, TaskStatus.completed)

    @requires_delegated(
        "Tasks.Read",
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_07_get_task_by_id(self):
        """Getting a task by ID returns the task with updated properties."""
        task = TestTaskList.task
        if not task or not task.id:
            self.skipTest("No task created from previous test")

        result = self.client.me.todo.lists[TestTaskList.task_list.id].tasks[task.id].get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.get_property("title"), "SDK Updated Task Title")

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_08_add_checklist_item(self):
        """Adding a checklist item (subtask) to a task should succeed."""
        task = TestTaskList.task
        if not task:
            self.skipTest("No task created from previous test")

        item = task.checklist_items.add(displayName="SDK Subtask").execute_query()
        self.assertIsNotNone(item.resource_path)
        self.assertEqual(item.display_name, "SDK Subtask")

    @requires_delegated(
        "Tasks.Read",
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_09_linked_resources_accessible(self):
        """A task should have a linkedResources collection accessible."""
        task = TestTaskList.task
        if not task:
            self.skipTest("No task created from previous test")

        resources = task.linked_resources.get().execute_query()
        self.assertIsNotNone(resources)

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_09a_attach_file(self):
        """Attaching a small file to a task should succeed and be listable/deletable."""
        task = TestTaskList.task
        if not task:
            self.skipTest("No task created from previous test")

        attachment = task.upload_attachment(b"hello world", name="sdk.txt", content_type="text/plain")
        self.assertIsNotNone(attachment.id)

        attachments = task.attachments.get().execute_query()
        self.assertGreaterEqual(len(attachments), 1)
        attachment.delete_object().execute_query()

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_10_delete_task(self):
        """Deleting an individual task should succeed."""
        task = TestTaskList.task
        if not task:
            self.skipTest("No task created from previous test")

        task.delete_object().execute_query()
        TestTaskList.task = None

    @requires_delegated(
        "Tasks.ReadWrite",
        bypass_roles=["Global Administrator"],
    )
    def test_11_delete_task_list(self):
        """Deleting the task list should succeed."""
        tl = TestTaskList.task_list
        if not tl:
            self.skipTest("No task list created from previous test")

        tl.delete_object().execute_query()
        TestTaskList.task_list = None

    @classmethod
    def tearDownClass(cls):
        tl = cls.task_list
        if tl and tl.resource_path:
            try:
                tl.delete_object().execute_query()
            except Exception:
                pass
        task = cls.task
        if task and task.resource_path:
            try:
                task.delete_object().execute_query()
            except Exception:
                pass
