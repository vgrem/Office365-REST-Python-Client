from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.entity_collection import EntityCollection
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.print.shares.share import PrinterShare


@dataclass
class UserPrint(ClientValue):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserPrint"

    recentPrinterShares: EntityCollection[PrinterShare] | None = None
