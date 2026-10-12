from __future__ import annotations

from datetime import datetime
from typing import Dict, cast

from office365.delta_collection import DeltaCollection
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.mail.importance import Importance
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.todo.tasks.task import TodoTask


class TodoTaskCollection(DeltaCollection[TodoTask]):
    """ """

    def __init__(self, context, resource_path=None):
        super().__init__(context, TodoTask, resource_path)

    def find_by_title(self, title: str, *, required: bool = False) -> TodoTask:
        """Look up a task by its ``title``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        task matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            title (str): The task title
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"title eq '{escape_odata_string(title)}'", required=required)

    def ensure(self, title: str) -> TodoTask:
        """Return the task with the given title, creating it when absent (idempotent).

        Deferred — resolve with ``execute_query()``. To Do task titles are **not**
        unique, so unlike the create-first helpers this looks the task up first
        and only creates it when the lookup comes back empty (the first match
        wins when several share the title):

            task = task_list.tasks.ensure("Prepare the demo").execute_query()

        Args:
            title (str): The task title

        Returns:
            TodoTask: The existing or newly created task
        """
        return_type = TodoTask(self.context, EntityPath(None, self.resource_path))
        return_type.set_property("title", title)
        self.add_child(return_type)

        def _ensure(col: TodoTaskCollection):
            if len(col) == 0:
                qry = CreateEntityQuery(self, cast(Dict, return_type.to_json()), return_type)
                self.context.add_query(qry)
            else:
                return_type.copy_from(col[0])

        self.get().filter(f"title eq '{escape_odata_string(title)}'").after_execute(_ensure)
        return return_type

    def add(
        self,
        title: str,
        due_date_time: datetime | DateTimeTimeZone | None = None,
        importance: Importance | None = None,
        body: str | ItemBody | None = None,
        **kwargs,
    ):
        return_type = TodoTask(self.context, EntityPath(None, self.resource_path))
        return_type.set_property("title", title)

        if due_date_time is not None:
            if isinstance(due_date_time, datetime):
                return_type.set_property("dueDateTime", DateTimeTimeZone.parse(due_date_time))
            elif isinstance(due_date_time, DateTimeTimeZone):
                return_type.set_property("dueDateTime", due_date_time)

        if importance is not None:
            return_type.set_property("importance", importance)

        if body is not None:
            if isinstance(body, str):
                return_type.set_property("body", ItemBody.text(body))
            elif isinstance(body, ItemBody):
                return_type.set_property("body", body)

        for key, value in kwargs.items():
            return_type.set_property(key, value)

        qry = CreateEntityQuery(self, cast(Dict, return_type.to_json()), return_type)
        self.context.add_query(qry)
        return return_type
