from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.extensions.extension import Extension
    from office365.intune.print.taskstatus import TaskStatus
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.importance import Importance
    from office365.outlook.mail.item_body import ItemBody
    from office365.outlook.mail.patterned_recurrence import PatternedRecurrence
    from office365.todo.attachments.base import AttachmentBase
    from office365.todo.attachments.session import AttachmentSession
    from office365.todo.checklist_item import ChecklistItem
    from office365.todo.linked_resource import LinkedResource


class TodoTask(Entity):
    @property
    def body(self) -> ItemBody:
        """Gets the body property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("body", ItemBody())

    @property
    def body_last_modified_date_time(self) -> Optional[datetime]:
        """Gets the bodyLastModifiedDateTime property"""
        return self.properties.get("bodyLastModifiedDateTime", datetime.min)

    @property
    def categories(self) -> StringCollection:
        """Gets the categories property"""
        return self.properties.get("categories", StringCollection())

    @property
    def completed_date_time(self) -> DateTimeTimeZone:
        """Gets the completedDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("completedDateTime", DateTimeTimeZone())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def due_date_time(self) -> DateTimeTimeZone:
        """Gets the dueDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("dueDateTime", DateTimeTimeZone())

    @property
    def has_attachments(self) -> Optional[bool]:
        """Gets the hasAttachments property"""
        return self.properties.get("hasAttachments", None)

    @property
    def importance(self) -> Importance:
        """Gets the importance property"""
        from office365.outlook.mail.importance import Importance

        return self.properties.get("importance", Importance.low)

    @property
    def is_reminder_on(self) -> Optional[bool]:
        """Gets the isReminderOn property"""
        return self.properties.get("isReminderOn", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def recurrence(self) -> PatternedRecurrence:
        """Gets the recurrence property"""
        from office365.outlook.mail.patterned_recurrence import PatternedRecurrence

        return self.properties.get("recurrence", PatternedRecurrence())

    @property
    def reminder_date_time(self) -> DateTimeTimeZone:
        """Gets the reminderDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("reminderDateTime", DateTimeTimeZone())

    @property
    def start_date_time(self) -> DateTimeTimeZone:
        """Gets the startDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("startDateTime", DateTimeTimeZone())

    @property
    def status(self) -> TaskStatus:
        """Gets the status property"""
        from office365.intune.print.taskstatus import TaskStatus

        return self.properties.get("status", TaskStatus.notStarted)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def attachments(self) -> EntityCollection[AttachmentBase]:
        """Gets the attachments property"""
        from office365.todo.attachments.base import AttachmentBase

        return self.properties.get(
            "attachments",
            EntityCollection[AttachmentBase](
                self.context, AttachmentBase, ResourcePath("attachments", self.resource_path)
            ),
        )

    @property
    def attachment_sessions(self) -> EntityCollection[AttachmentSession]:
        """Gets the attachmentSessions property"""
        from office365.todo.attachments.session import AttachmentSession

        return self.properties.get(
            "attachmentSessions",
            EntityCollection[AttachmentSession](
                self.context, AttachmentSession, ResourcePath("attachmentSessions", self.resource_path)
            ),
        )

    @property
    def checklist_items(self) -> EntityCollection[ChecklistItem]:
        """Gets the checklistItems property"""
        from office365.todo.checklist_item import ChecklistItem

        return self.properties.get(
            "checklistItems",
            EntityCollection[ChecklistItem](
                self.context, ChecklistItem, ResourcePath("checklistItems", self.resource_path)
            ),
        )

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """Gets the extensions property"""
        from office365.directory.extensions.extension import Extension

        return self.properties.get(
            "extensions",
            EntityCollection[Extension](self.context, Extension, ResourcePath("extensions", self.resource_path)),
        )

    @property
    def linked_resources(self) -> EntityCollection[LinkedResource]:
        """Gets the linkedResources property"""
        from office365.todo.linked_resource import LinkedResource

        return self.properties.get(
            "linkedResources",
            EntityCollection[LinkedResource](
                self.context, LinkedResource, ResourcePath("linkedResources", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TodoTask"
