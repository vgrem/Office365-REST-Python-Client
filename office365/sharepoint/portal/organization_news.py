from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.portal.organization_news import (
        OrganizationNewsSiteReference,
    )


@dataclass
class OrganizationNewsSiteReference(ClientValue):
    pass


class OrganizationNews(Entity):
    def sites_reference(self):
        return_type = ClientResult(self.context, ClientValueCollection(OrganizationNewsSiteReference))
        qry = ServiceOperationQuery(self, "SitesReference", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_site_reference(
        context: ClientContext, org_news_site_url: str, validate: bool
    ) -> ClientResult[OrganizationNewsSiteReference]:
        """GetSiteReference operation.

        Args:
            org_news_site_url (str):
                orgNewsSiteUrl parameter
            validate (bool):
                validate parameter
        """
        from office365.sharepoint.portal.organization_news import (
            OrganizationNews,
            OrganizationNewsSiteReference,
        )

        return_type = ClientResult(context, OrganizationNewsSiteReference())
        qry = ServiceOperationQuery(
            OrganizationNews(context),
            "GetSiteReference",
            None,
            {"orgNewsSiteUrl": org_news_site_url, "validate": validate},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
