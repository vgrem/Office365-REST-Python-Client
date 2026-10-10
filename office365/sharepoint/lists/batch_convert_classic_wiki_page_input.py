from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class BatchConvertClassicWikiPageInput(ClientValue):
    order: float | None = None
    sourceItemId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.SmartWikiLibrary.BatchConvertClassicWikiPageInput"
