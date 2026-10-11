from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.integer_range import IntegerRange
from office365.intune.print.colormode import PrintColorMode
from office365.intune.print.duplexmode import PrintDuplexMode
from office365.intune.print.finishing import PrintFinishing
from office365.intune.print.multipagelayout import PrintMultipageLayout
from office365.intune.print.orientation import PrintOrientation
from office365.intune.print.printers.feedorientation import PrinterFeedOrientation
from office365.intune.print.quality import PrintQuality
from office365.intune.print.scaling import PrintScaling
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection


@dataclass
class PrinterCapabilities(ClientValue):
    """Represents the capabilities reported by a printer/printerShare."""

    bottomMargins: ClientValueCollection = field(default_factory=ClientValueCollection)

    collation: bool | None = None

    colorModes: ClientValueCollection[PrintColorMode] = field(
        default_factory=lambda: ClientValueCollection(PrintColorMode)
    )

    contentTypes: StringCollection = field(default_factory=StringCollection)

    dpis: ClientValueCollection = field(default_factory=ClientValueCollection)

    duplexModes: ClientValueCollection[PrintDuplexMode] = field(
        default_factory=lambda: ClientValueCollection(PrintDuplexMode)
    )

    feedOrientations: ClientValueCollection[PrinterFeedOrientation] = field(
        default_factory=lambda: ClientValueCollection(PrinterFeedOrientation)
    )

    finishings: ClientValueCollection[PrintFinishing] = field(
        default_factory=lambda: ClientValueCollection(PrintFinishing)
    )

    inputBins: StringCollection = field(default_factory=StringCollection)

    isColorPrintingSupported: bool | None = None

    isPageRangeSupported: bool | None = None

    leftMargins: ClientValueCollection = field(default_factory=ClientValueCollection)

    mediaColors: StringCollection = field(default_factory=StringCollection)

    mediaSizes: StringCollection = field(default_factory=StringCollection)

    mediaTypes: StringCollection = field(default_factory=StringCollection)

    multipageLayouts: ClientValueCollection[PrintMultipageLayout] = field(
        default_factory=lambda: ClientValueCollection(PrintMultipageLayout)
    )

    orientations: ClientValueCollection[PrintOrientation] = field(
        default_factory=lambda: ClientValueCollection(PrintOrientation)
    )

    outputBins: StringCollection = field(default_factory=StringCollection)

    pagesPerSheet: ClientValueCollection = field(default_factory=ClientValueCollection)

    qualities: ClientValueCollection[PrintQuality] = field(default_factory=lambda: ClientValueCollection(PrintQuality))

    rightMargins: ClientValueCollection = field(default_factory=ClientValueCollection)

    scalings: ClientValueCollection[PrintScaling] = field(default_factory=lambda: ClientValueCollection(PrintScaling))

    supportsFitPdfToPage: bool | None = None

    topMargins: ClientValueCollection = field(default_factory=ClientValueCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterCapabilities"

    copiesPerJob: IntegerRange = field(default_factory=IntegerRange)
