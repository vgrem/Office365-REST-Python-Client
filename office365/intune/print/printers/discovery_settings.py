from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.print.air_print_settings import AirPrintSettings
from office365.runtime.client_value import ClientValue


@dataclass
class PrinterDiscoverySettings(ClientValue):
    airPrint: AirPrintSettings = field(default_factory=AirPrintSettings)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterDiscoverySettings"
