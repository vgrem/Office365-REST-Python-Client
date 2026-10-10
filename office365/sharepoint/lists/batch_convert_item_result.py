from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.lists.batch_convert_asset_result import (
    BatchConvertAssetResult,
)
from office365.sharepoint.lists.conversion_loss_report import ConversionLossReport


@dataclass
class BatchConvertItemResult(ClientValue):
    errorCode: str | None = None
    errorMessage: str | None = None
    lossy: ConversionLossReport = field(default_factory=ConversionLossReport)
    sourceItemId: int | None = None
    succeeded: bool | None = None
    viewerUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.SmartWikiLibrary.BatchConvertItemResult"

    assets: ClientValueCollection[BatchConvertAssetResult] = field(
        default_factory=lambda: ClientValueCollection(BatchConvertAssetResult)
    )

    rollbackTargetBranchServerRelativeUrl: str | None = None

    rollbackTargetListId: UUID | None = None

    rollbackTargetPageItemId: int | None = None

    rollbackTargetPageServerRelativeUrl: str | None = None

    rollbackTargetPageUniqueId: UUID | None = None
