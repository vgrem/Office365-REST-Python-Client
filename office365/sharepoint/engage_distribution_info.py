from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class EngageDistributionInfo(ClientValue):
    AssetsFolderName: str | None = None
    DestinationId: str | None = None
    DistributedDate: datetime | None = None
    OwnerId: str | None = None
    RawThreadId: str | None = None
    ThreadId: str | None = None
    ThreadStarterId: str | None = None
