from __future__ import annotations

import os
from datetime import datetime
from os import PathLike
from typing import IO, Optional, Union

from office365.directory.extensions.extension import Extension
from office365.directory.extensions.open_type import OpenTypeExtension
from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.mail.importance import Importance
from office365.outlook.mail.item_body import ItemBody
from office365.outlook.mail.patterned_recurrence import PatternedRecurrence
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.todo.attachments.collection import AttachmentBaseCollection
from office365.todo.attachments.session import AttachmentSession
from office365.todo.attachments.task_file import TaskFileAttachment
from office365.todo.checklist_item import ChecklistItem
from office365.todo.linked_resource import LinkedResource
from office365.todo.tasks.taskstatus import TaskStatus

DEFAULT_ATTACHMENT_CHUNK_SIZE = 4 * 1024 * 1024
MAX_SIMPLE_ATTACHMENT_BYTES = 3 * 1024 * 1024


def _stream_size(stream: IO) -> int:
    """Byte length of a seekable stream (file or ``io.BytesIO``), preserving position."""
    try:
        return os.fstat(stream.fileno()).st_size
    except (AttributeError, OSError):
        position = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(position)
        return size


class TodoTask(Entity):
    """A todoTask represents a task, such as a piece of work or personal item, that can be tracked and completed."""

    def __str__(self) -> str:
        return self.title or self.entity_type_name or ""

    @property
    def body(self) -> ItemBody:
        """The task body that typically contains information about the task."""
        return self.properties.get("body", ItemBody())

    @odata(name="bodyLastModifiedDateTime")
    @property
    def body_last_modified_date_time(self) -> Optional[datetime]:
        """The date and time when the task body was last modified."""
        return self.properties.get("bodyLastModifiedDateTime", None)

    @odata(name="categories")
    @property
    def categories(self) -> StringCollection:
        """The categories associated with the task."""
        return self.properties.get("categories", StringCollection())

    @odata(name="completedDateTime")
    @property
    def completed_date_time(self) -> DateTimeTimeZone:
        """The date and time when the task was completed."""
        return self.properties.get("completedDateTime", DateTimeTimeZone())

    @odata(name="createdDateTime")
    @property
    def created_date_time(self) -> datetime:
        """The date and time when the task was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @odata(name="dueDateTime")
    @property
    def due_date_time(self) -> DateTimeTimeZone:
        """The date and time when the task is due."""
        return self.properties.get("dueDateTime", DateTimeTimeZone())

    @odata(name="hasAttachments")
    @property
    def has_attachments(self) -> Optional[bool]:
        """Indicates whether the task has attachments."""
        return self.properties.get("hasAttachments", None)

    @odata(name="importance")
    @property
    def importance(self) -> Optional[Importance]:
        """The importance of the task. Possible values: low, normal, high."""
        return self.properties.get("importance", None)

    @odata(name="isReminderOn")
    @property
    def is_reminder_on(self) -> Optional[bool]:
        """Indicates whether a reminder is on for the task."""
        return self.properties.get("isReminderOn", None)

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_date_time(self) -> datetime:
        """The date and time when the task was last modified."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @odata(name="recurrence")
    @property
    def recurrence(self) -> Optional[PatternedRecurrence]:
        """The recurrence pattern for the task."""
        return self.properties.get("recurrence", None)

    @odata(name="reminderDateTime")
    @property
    def reminder_date_time(self) -> DateTimeTimeZone:
        """The date and time for the reminder of the task."""
        return self.properties.get("reminderDateTime", DateTimeTimeZone())

    @odata(name="startDateTime")
    @property
    def start_date_time(self) -> DateTimeTimeZone:
        """The date and time when the task is scheduled to start."""
        return self.properties.get("startDateTime", DateTimeTimeZone())

    @odata(name="status")
    @property
    def status(self) -> Optional[TaskStatus]:
        """The status of the task. Possible values: notStarted, inProgress, completed, waitingOnOthers, deferred."""
        return self.properties.get("status", None)

    @status.setter
    def status(self, value: TaskStatus):
        self.set_property("status", value)

    @property
    def title(self) -> Optional[str]:
        """A brief description of the task."""
        return self.properties.get("title", None)

    @title.setter
    def title(self, value):
        self.set_property("title", value)

    @property
    def attachment_sessions(self) -> EntityCollection[AttachmentSession]:
        """A collection of attachment sessions for the task."""
        return self.properties.get(
            "attachmentSessions",
            EntityCollection(
                self.context,
                AttachmentSession,
                ResourcePath("attachmentSessions", self.resource_path),
            ),
        )

    @property
    def attachments(self) -> AttachmentBaseCollection:
        """A collection of file attachments for the task."""
        return self.properties.get(
            "attachments",
            AttachmentBaseCollection(self.context, ResourcePath("attachments", self.resource_path)),
        )

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """The collection of open extensions defined for the task."""
        return self.properties.get(
            "extensions",
            EntityCollection(self.context, Extension, ResourcePath("extensions", self.resource_path)),
        )

    @odata(name="checklistItems")
    @property
    def checklist_items(self) -> EntityCollection[ChecklistItem]:
        """A collection of checklistItems linked to a task."""
        return self.properties.get(
            "checklistItems",
            EntityCollection(
                self.context,
                ChecklistItem,
                ResourcePath("checklistItems", self.resource_path),
            ),
        )

    @odata(name="linkedResources")
    @property
    def linked_resources(self) -> EntityCollection[LinkedResource]:
        """A collection of resources linked to the task."""
        return self.properties.get(
            "linkedResources",
            EntityCollection(
                self.context,
                LinkedResource,
                ResourcePath("linkedResources", self.resource_path),
            ),
        )

    @require_permission(delegated=["Tasks.ReadWrite"])
    def upload_attachment(
        self,
        source: Union[str, PathLike, bytes, bytearray, IO],
        name: Optional[str] = None,
        content_type: Optional[str] = None,
        chunk_size: int = DEFAULT_ATTACHMENT_CHUNK_SIZE,
        progress=None,
    ) -> TaskFileAttachment:
        """Attach a file to the task, dispatching by size.

        Files up to 3 MB are posted as a ``taskFileAttachment``; larger ones
        (up to 25 MB) use an upload session and chunked upload.

        Args:
            source: Path, raw bytes, or a binary stream.
            name (str): Display name of the attachment (defaults to the file name).
            content_type (str): MIME type of the attachment.
            chunk_size (int): Upload-session chunk size (4 MB by default).
            progress: Optional per-chunk ``Progress`` hook for session uploads.
        """
        stream: Optional[IO] = None
        if isinstance(source, (bytes, bytearray)):
            content: Optional[bytes] = bytes(source)
            size: Optional[int] = len(source)
            default_name = None
        elif isinstance(source, (str, PathLike)):
            content = None
            size = os.path.getsize(source)
            default_name = os.path.basename(str(source))
        else:
            stream = source
            content = None
            size = _stream_size(stream)
            default_name = os.path.basename(getattr(stream, "name", "") or "")

        attachment_name = name or default_name or "attachment"
        if size is not None and size <= MAX_SIMPLE_ATTACHMENT_BYTES:
            if content is None:
                if stream is None:
                    with open(str(source), "rb") as file_object:
                        content = file_object.read()
                else:
                    position = stream.tell()
                    stream.seek(0)
                    content = stream.read()
                    stream.seek(position)
            assert content is not None
            return self.attachments.add(attachment_name, content, content_type, size).execute_query()

        session = self.attachments.create_upload_session(attachment_name, size or 0, content_type).execute_query()
        return session.upload(source, chunk_size=chunk_size, progress=progress)

    @require_permission(delegated=["Tasks.ReadWrite"])
    def add_extension(self, name: str, **properties) -> OpenTypeExtension:
        """Create an open type extension on the task.

        Args:
            name (str): Unique text identifier (``extensionName``).
            **properties: Additional custom properties to store on the extension.
        """
        return_type = OpenTypeExtension(self.context)
        return_type.set_property("extensionName", name)
        for key, value in properties.items():
            return_type.set_property(key, value)
        self.extensions.add_child(return_type)
        qry = CreateEntityQuery(self.extensions, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore
