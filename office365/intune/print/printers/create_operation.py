from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.intune.print.printers.printer import Printer


class PrinterCreateOperation(PollableOperation, Entity):
    @property
    def certificate(self) -> Optional[str]:
        """Gets the certificate property"""
        return self.properties.get("certificate", None)

    @property
    def printer(self) -> Printer:
        """Gets the printer property"""
        from office365.intune.print.printers.printer import Printer

        return self.properties.get("printer", Printer(self.context, ResourcePath("printer", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterCreateOperation"
