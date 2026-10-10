from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class SPOFileArchivePolicyInfo(ClientValue):
    CreatedBy: str | None = None
    CreatedOn: datetime | None = field(default_factory=lambda: datetime.min)
    FileTypeCriteria: StringCollection = field(default_factory=StringCollection)
    LastAccessDateCriteria: int | None = None
    LastModifiedBy: str | None = None
    LastRunDate: datetime | None = field(default_factory=lambda: datetime.min)
    ModifiedDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    Name: str | None = None
    PolicyId: UUID | None = None
    PolicyType: str | None = None
    SiteCount: int | None = None
    State: str | None = None
    WhatIfMode: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOFileArchivePolicyInfo"

    FileTypeExclusionCriteria: StringCollection = field(default_factory=StringCollection)
