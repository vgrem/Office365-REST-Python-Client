from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.copilot.agentinsights.report_metadata import (
        SPOCopilotAgentInsightsReportMetadata,
    )
    from office365.sharepoint.tenant.administration.copilot.agentinsightscopilotagentsonsitesdetails import (
        SPOCopilotAgentInsightsCopilotAgentsOnSitesDetails,
    )
    from office365.sharepoint.tenant.administration.copilot.agentinsightssitedistribution import (
        SPOCopilotAgentInsightsSiteDistribution,
    )
    from office365.sharepoint.tenant.administration.copilot.agentinsightstopsitesdetails import (
        SPOCopilotAgentInsightsTopSitesDetails,
    )


class SPOCopilotAgentInsightsRestApiClient(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOCopilotAgentInsightsRestApiClient"

    def create_copilot_agent_insights_report(
        self, report_period: int
    ) -> ClientResult[SPOCopilotAgentInsightsReportMetadata]:
        """CreateCopilotAgentInsightsReport operation.

        Args:
            report_period (int):
                reportPeriod parameter
        """
        from office365.sharepoint.tenant.administration.copilot.agentinsights.report_metadata import (
            SPOCopilotAgentInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, SPOCopilotAgentInsightsReportMetadata())
        qry = ServiceOperationQuery(
            self, "CreateCopilotAgentInsightsReport", None, {"reportPeriod": report_period}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_copilot_agent_insights_full_report_content(
        self, report_id: UUID, report_sub_type: str, is_full_details: bool
    ) -> ClientResult[str]:
        """GetCopilotAgentInsightsFullReportContent operation.

        Args:
            report_id (UUID):
                reportId parameter
            report_sub_type (str):
                reportSubType parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetCopilotAgentInsightsFullReportContent",
            None,
            {"reportId": report_id, "reportSubType": report_sub_type, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_copilot_agents_on_sites_top_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOCopilotAgentInsightsCopilotAgentsOnSitesDetails]]:
        """GetCopilotAgentsOnSitesTopDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenant.administration.copilot.agentinsightscopilotagentsonsitesdetails import (
            SPOCopilotAgentInsightsCopilotAgentsOnSitesDetails,
        )

        return_type = ClientResult(
            self.context, ClientValueCollection[SPOCopilotAgentInsightsCopilotAgentsOnSitesDetails]()
        )
        qry = ServiceOperationQuery(
            self,
            "GetCopilotAgentsOnSitesTopDetails",
            None,
            {"reportId": report_id, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_site_distributions_top_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOCopilotAgentInsightsSiteDistribution]]:
        """GetSiteDistributionsTopDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenant.administration.copilot.agentinsightssitedistribution import (
            SPOCopilotAgentInsightsSiteDistribution,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOCopilotAgentInsightsSiteDistribution]())
        qry = ServiceOperationQuery(
            self,
            "GetSiteDistributionsTopDetails",
            None,
            {"reportId": report_id, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_top_sites_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOCopilotAgentInsightsTopSitesDetails]]:
        """GetTopSitesDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenant.administration.copilot.agentinsightstopsitesdetails import (
            SPOCopilotAgentInsightsTopSitesDetails,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOCopilotAgentInsightsTopSitesDetails]())
        qry = ServiceOperationQuery(
            self,
            "GetTopSitesDetails",
            None,
            {"reportId": report_id, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_all_copilot_agent_insights_reports_metadata(
        self,
    ) -> ClientResult[ClientValueCollection[SPOCopilotAgentInsightsReportMetadata]]:
        """GetAllCopilotAgentInsightsReportsMetadata operation."""
        from office365.sharepoint.tenant.administration.copilot.agentinsights.report_metadata import (
            SPOCopilotAgentInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOCopilotAgentInsightsReportMetadata]())
        qry = ServiceOperationQuery(self, "GetAllCopilotAgentInsightsReportsMetadata", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type
