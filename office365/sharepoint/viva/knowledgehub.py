from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.viva.knowledgehubsitereference import (
        KnowledgeHubSiteReference,
    )


class KnowledgeHub(Entity):
    def add_or_update_site_reference(self, knowledge_hub_site_url: str) -> Self:
        """AddOrUpdateSiteReference operation.

        Args:
            knowledge_hub_site_url (str):
                knowledgeHubSiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "AddOrUpdateSiteReference", None, {"knowledgeHubSiteUrl": knowledge_hub_site_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def site_reference(self) -> ClientResult[KnowledgeHubSiteReference]:
        """SiteReference operation."""
        from office365.sharepoint.viva.knowledgehubsitereference import (
            KnowledgeHubSiteReference,
        )

        return_type = ClientResult(self.context, KnowledgeHubSiteReference())
        qry = FunctionQuery(self, "SiteReference", [], return_type)
        self.context.add_query(qry)
        return return_type
