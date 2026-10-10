from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.spdatagovernancesarstartsitereviewresponse import (
        SPDataGovernanceSARStartSiteReviewResponse,
    )
    from office365.sharepoint.tenant.administration.spdatagovernancesitereviewsresponse import (
        SPDataGovernanceSiteReviewsResponse,
    )


class SPDataGovernanceSARRestApiClient(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPDataGovernanceSARRestApiClient"

    def get_spo_site_review(
        self, report_entity: int, site_reviewtatus: int, site_review_id: UUID, site_id: UUID
    ) -> ClientResult[ClientValueCollection[SPDataGovernanceSiteReviewsResponse]]:
        """GetSPOSiteReview operation.

        Args:
            report_entity (int):
                reportEntity parameter
            site_reviewtatus (int):
                siteReviewtatus parameter
            site_review_id (UUID):
                siteReviewID parameter
            site_id (UUID):
                siteID parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernancesitereviewsresponse import (
            SPDataGovernanceSiteReviewsResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPDataGovernanceSiteReviewsResponse]())
        qry = ServiceOperationQuery(
            self,
            "GetSPOSiteReview",
            None,
            {
                "reportEntity": report_entity,
                "siteReviewtatus": site_reviewtatus,
                "siteReviewID": site_review_id,
                "siteID": site_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def start_spo_site_review(
        self, detailed_source_report_id: UUID, site_id: UUID, admin_comment: str
    ) -> ClientResult[SPDataGovernanceSARStartSiteReviewResponse]:
        """StartSPOSiteReview operation.

        Args:
            detailed_source_report_id (UUID):
                detailedSourceReportId parameter
            site_id (UUID):
                siteId parameter
            admin_comment (str):
                adminComment parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernancesarstartsitereviewresponse import (
            SPDataGovernanceSARStartSiteReviewResponse,
        )

        return_type = ClientResult(self.context, SPDataGovernanceSARStartSiteReviewResponse())
        qry = ServiceOperationQuery(
            self,
            "StartSPOSiteReview",
            None,
            {"detailedSourceReportId": detailed_source_report_id, "siteId": site_id, "adminComment": admin_comment},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
