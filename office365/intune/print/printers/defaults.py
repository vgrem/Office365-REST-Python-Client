from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.print.colormode import PrintColorMode
from office365.intune.print.duplexmode import PrintDuplexMode
from office365.intune.print.finishing import PrintFinishing
from office365.intune.print.multipagelayout import PrintMultipageLayout
from office365.intune.print.orientation import PrintOrientation
from office365.intune.print.quality import PrintQuality
from office365.intune.print.scaling import PrintScaling
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class PrinterDefaults(ClientValue):
    colorMode: PrintColorMode = PrintColorMode.blackAndWhite
    contentType: str | None = None
    copiesPerJob: int | None = None
    dpi: int | None = None
    duplexMode: PrintDuplexMode = PrintDuplexMode.flipOnLongEdge
    finishings: ClientValueCollection[PrintFinishing] = field(
        default_factory=lambda: ClientValueCollection(PrintFinishing)
    )
    fitPdfToPage: bool | None = None
    inputBin: str | None = None
    mediaColor: str | None = None
    mediaSize: str | None = None
    mediaType: str | None = None
    multipageLayout: PrintMultipageLayout = PrintMultipageLayout.clockwiseFromTopLeft
    orientation: PrintOrientation = PrintOrientation.portrait
    outputBin: str | None = None
    pagesPerSheet: int | None = None
    quality: PrintQuality = PrintQuality.low
    scaling: PrintScaling = PrintScaling.auto

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterDefaults"
