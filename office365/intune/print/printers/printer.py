from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.intune.print.printers.base import PrinterBase
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.print.connectors.connector import PrintConnector
    from office365.intune.print.shares.share import PrinterShare
    from office365.intune.print.task_trigger import PrintTaskTrigger


class Printer(PrinterBase):
    """Represents a printer device that has been registered with the Universal Print service.
    Printer resources can be used to manage print jobs, printer settings, printer metadata and registration status.
    """

    @property
    def has_physical_device(self) -> Optional[bool]:
        """Gets the hasPhysicalDevice property"""
        return self.properties.get("hasPhysicalDevice", None)

    @property
    def is_shared(self) -> Optional[bool]:
        """Gets the isShared property"""
        return self.properties.get("isShared", None)

    @property
    def last_seen_date_time(self) -> Optional[datetime]:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def registered_date_time(self) -> Optional[datetime]:
        """Gets the registeredDateTime property"""
        return self.properties.get("registeredDateTime", datetime.min)

    @property
    def connectors(self) -> EntityCollection[PrintConnector]:
        """Gets the connectors property"""
        from office365.intune.print.connectors.connector import PrintConnector

        return self.properties.get(
            "connectors",
            EntityCollection[PrintConnector](
                self.context, PrintConnector, ResourcePath("connectors", self.resource_path)
            ),
        )

    @property
    def shares(self) -> EntityCollection[PrinterShare]:
        """Gets the shares property"""
        from office365.intune.print.shares.share import PrinterShare

        return self.properties.get(
            "shares",
            EntityCollection[PrinterShare](self.context, PrinterShare, ResourcePath("shares", self.resource_path)),
        )

    @property
    def task_triggers(self) -> EntityCollection[PrintTaskTrigger]:
        """Gets the taskTriggers property"""
        from office365.intune.print.task_trigger import PrintTaskTrigger

        return self.properties.get(
            "taskTriggers",
            EntityCollection[PrintTaskTrigger](
                self.context, PrintTaskTrigger, ResourcePath("taskTriggers", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Printer"
