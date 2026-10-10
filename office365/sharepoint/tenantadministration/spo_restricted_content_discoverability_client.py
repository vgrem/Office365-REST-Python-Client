from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.insights.reportmetadata import (
        SPOInsightsReportMetadata,
    )
    from office365.sharepoint.tenant.administration.sporestrictedcontentdiscoverabilitysitedetails import (
        SPORestrictedContentDiscoverabilitySiteDetails,
    )


class SPORestrictedContentDiscoverabilityClient(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPORestrictedContentDiscoverabilityClient"

    def create_restricted_content_discoverability_report(self) -> ClientResult[SPOInsightsReportMetadata]:
        """CreateRestrictedContentDiscoverabilityReport operation."""
        from office365.sharepoint.tenant.administration.insights.reportmetadata import (
            SPOInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, SPOInsightsReportMetadata())
        qry = ServiceOperationQuery(self, "CreateRestrictedContentDiscoverabilityReport", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_restricted_content_discoverability_reports(
        self,
    ) -> ClientResult[ClientValueCollection[SPOInsightsReportMetadata]]:
        """GetAllRestrictedContentDiscoverabilityReports operation."""
        from office365.sharepoint.tenant.administration.insights.reportmetadata import (
            SPOInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOInsightsReportMetadata]())
        qry = ServiceOperationQuery(self, "GetAllRestrictedContentDiscoverabilityReports", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_restrict_content_org_wide_search_usage_insights_report_content(
        self, report_id: UUID
    ) -> ClientResult[ClientValueCollection[SPORestrictedContentDiscoverabilitySiteDetails]]:
        """GetRestrictContentOrgWideSearchUsageInsightsReportContent operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        from office365.sharepoint.tenant.administration.sporestrictedcontentdiscoverabilitysitedetails import (
            SPORestrictedContentDiscoverabilitySiteDetails,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPORestrictedContentDiscoverabilitySiteDetails]())
        qry = ServiceOperationQuery(
            self,
            "GetRestrictContentOrgWideSearchUsageInsightsReportContent",
            None,
            {"reportId": report_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_data_access_governance_insight_by_id(self, report_id: UUID) -> ClientResult[SPOInsightsReportMetadata]:
        """GetSPODataAccessGovernanceInsightById operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        from office365.sharepoint.tenant.administration.insights.reportmetadata import (
            SPOInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, SPOInsightsReportMetadata())
        qry = ServiceOperationQuery(
            self, "GetSPODataAccessGovernanceInsightById", None, {"reportId": report_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
