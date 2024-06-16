from datetime import datetime
from typing import List

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.tenant.administration.sites.creation_data import (
    SiteCreationData,
)


class SiteCreationSource(ClientValue):
    def __init__(
        self,
        IsSyncThresholdLimitReached=None,
        LastRefreshTimeStamp=None,
        site_creation_data=None,
        SyncThresholdLimit=None,
        TotalSitesCount=None,
    ):
        # type: (bool, datetime, List[SiteCreationData], int, int) -> None
        self.IsSyncThresholdLimitReached = IsSyncThresholdLimitReached
        self.LastRefreshTimeStamp = LastRefreshTimeStamp
        self.SiteCreationData = ClientValueCollection(
            SiteCreationData, site_creation_data
        )
        self.SyncThresholdLimit = SyncThresholdLimit
        self.TotalSitesCount = TotalSitesCount

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteCreationSource"
