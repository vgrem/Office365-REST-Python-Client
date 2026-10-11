from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.print.connectors.connector import PrintConnector
from office365.intune.print.shares.share import PrinterShare
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.print.operation import PrintOperation
    from office365.intune.print.printers.printer import Printer
    from office365.intune.print.services.service import PrintService
    from office365.intune.print.settings import PrintSettings
    from office365.intune.print.task_definition import PrintTaskDefinition


class Print(Entity):
    """When accompanied by a Universal Print subscription, the Print feature enables management of printers and
    discovery of printServiceEndpoints that can be used to manage printers and print jobs within Universal Print.
    """

    @property
    def connectors(self):
        """The list of available print connectors."""
        return self.properties.get(
            "connectors",
            EntityCollection(
                self.context,
                PrintConnector,
                ResourcePath("connectors", self.resource_path),
            ),
        )

    @property
    def shares(self):
        """The list of printer shares registered in the tenant."""
        return self.properties.get(
            "shares",
            EntityCollection(self.context, PrinterShare, ResourcePath("shares", self.resource_path)),
        )

    @property
    def settings(self) -> PrintSettings:
        """Gets the settings property"""
        from office365.intune.print.settings import PrintSettings

        return self.properties.get("settings", PrintSettings())

    @property
    def operations(self) -> EntityCollection[PrintOperation]:
        """Gets the operations property"""
        from office365.intune.print.operation import PrintOperation

        return self.properties.get(
            "operations",
            EntityCollection[PrintOperation](
                self.context, PrintOperation, ResourcePath("operations", self.resource_path)
            ),
        )

    @property
    def printers(self) -> EntityCollection[Printer]:
        """Gets the printers property"""
        from office365.intune.print.printers.printer import Printer

        return self.properties.get(
            "printers", EntityCollection[Printer](self.context, Printer, ResourcePath("printers", self.resource_path))
        )

    @property
    def services(self) -> EntityCollection[PrintService]:
        """Gets the services property"""
        from office365.intune.print.services.service import PrintService

        return self.properties.get(
            "services",
            EntityCollection[PrintService](self.context, PrintService, ResourcePath("services", self.resource_path)),
        )

    @property
    def task_definitions(self) -> EntityCollection[PrintTaskDefinition]:
        """Gets the taskDefinitions property"""
        from office365.intune.print.task_definition import PrintTaskDefinition

        return self.properties.get(
            "taskDefinitions",
            EntityCollection[PrintTaskDefinition](
                self.context, PrintTaskDefinition, ResourcePath("taskDefinitions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Print"
