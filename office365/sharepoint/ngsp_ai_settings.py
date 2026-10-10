from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.sites.site_ai_settings import SiteAISettings
    from office365.sharepoint.sites.site_ai_settings_request import (
        SiteAISettingsRequest,
    )


class NgspAISettings(Entity):
    def get_sites_ai_settings(
        self, requests: ClientValueCollection[SiteAISettingsRequest]
    ) -> ClientResult[ClientValueCollection[SiteAISettings]]:
        """GetSitesAISettings operation.

        Args:
            requests (ClientValueCollection[SiteAISettingsRequest]):
                requests parameter
        """
        from office365.sharepoint.sites.site_ai_settings import SiteAISettings

        return_type = ClientResult(self.context, ClientValueCollection[SiteAISettings]())
        qry = FunctionQuery(self, "GetSitesAISettings", [requests], return_type)
        self.context.add_query(qry)
        return return_type
