from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.users.identity import UserIdentity
    from office365.intune.print.document import PrintDocument
    from office365.intune.print.job_configuration import PrintJobConfiguration
    from office365.intune.print.job_status import PrintJobStatus
    from office365.intune.print.task import PrintTask


class PrintJob(Entity):
    @property
    def acknowledged_date_time(self) -> Optional[datetime]:
        """Gets the acknowledgedDateTime property"""
        return self.properties.get("acknowledgedDateTime", datetime.min)

    @property
    def configuration(self) -> PrintJobConfiguration:
        """Gets the configuration property"""
        from office365.intune.print.job_configuration import PrintJobConfiguration

        return self.properties.get("configuration", PrintJobConfiguration())

    @property
    def created_by(self) -> UserIdentity:
        """Gets the createdBy property"""
        from office365.directory.users.identity import UserIdentity

        return self.properties.get("createdBy", UserIdentity())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def error_code(self) -> Optional[int]:
        """Gets the errorCode property"""
        return self.properties.get("errorCode", None)

    @property
    def is_fetchable(self) -> Optional[bool]:
        """Gets the isFetchable property"""
        return self.properties.get("isFetchable", None)

    @property
    def redirected_from(self) -> Optional[str]:
        """Gets the redirectedFrom property"""
        return self.properties.get("redirectedFrom", None)

    @property
    def redirected_to(self) -> Optional[str]:
        """Gets the redirectedTo property"""
        return self.properties.get("redirectedTo", None)

    @property
    def status(self) -> PrintJobStatus:
        """Gets the status property"""
        from office365.intune.print.job_status import PrintJobStatus

        return self.properties.get("status", PrintJobStatus())

    @property
    def documents(self) -> EntityCollection[PrintDocument]:
        """Gets the documents property"""
        from office365.intune.print.document import PrintDocument

        return self.properties.get(
            "documents",
            EntityCollection[PrintDocument](self.context, PrintDocument, ResourcePath("documents", self.resource_path)),
        )

    @property
    def tasks(self) -> EntityCollection[PrintTask]:
        """Gets the tasks property"""
        from office365.intune.print.task import PrintTask

        return self.properties.get(
            "tasks", EntityCollection[PrintTask](self.context, PrintTask, ResourcePath("tasks", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintJob"
