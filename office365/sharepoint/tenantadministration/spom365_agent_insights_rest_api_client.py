from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.spom365agentinsightsm365agentsonsitesdetails import (
        SPOM365AgentInsightsM365AgentsOnSitesDetails,
    )
    from office365.sharepoint.tenant.administration.spom365agentinsightsreportmetadata import (
        SPOM365AgentInsightsReportMetadata,
    )
    from office365.sharepoint.tenant.administration.spom365agentinsightssitedistributiondetails import (
        SPOM365AgentInsightsSiteDistributionDetails,
    )
    from office365.sharepoint.tenantadministration.spom365_agent_insights_top20_agents_details import (
        SPOM365AgentInsightsTop20AgentsDetails,
    )


class SPOM365AgentInsightsRestApiClient(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOM365AgentInsightsRestApiClient"

    def create_m365_agent_insights_report(self, report_period: int) -> ClientResult[SPOM365AgentInsightsReportMetadata]:
        """CreateM365AgentInsightsReport operation.

        Args:
            report_period (int):
                reportPeriod parameter
        """
        from office365.sharepoint.tenant.administration.spom365agentinsightsreportmetadata import (
            SPOM365AgentInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, SPOM365AgentInsightsReportMetadata())
        qry = ServiceOperationQuery(
            self, "CreateM365AgentInsightsReport", None, {"reportPeriod": report_period}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_all_m365_agent_insights_reports_metadata(
        self,
    ) -> ClientResult[ClientValueCollection[SPOM365AgentInsightsReportMetadata]]:
        """GetAllM365AgentInsightsReportsMetadata operation."""
        from office365.sharepoint.tenant.administration.spom365agentinsightsreportmetadata import (
            SPOM365AgentInsightsReportMetadata,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOM365AgentInsightsReportMetadata]())
        qry = ServiceOperationQuery(self, "GetAllM365AgentInsightsReportsMetadata", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_m365_agent_insights_full_report_content(
        self, report_id: UUID, report_sub_type: str, is_full_details: bool
    ) -> ClientResult[str]:
        """GetM365AgentInsightsFullReportContent operation.

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
            "GetM365AgentInsightsFullReportContent",
            None,
            {"reportId": report_id, "reportSubType": report_sub_type, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_m365_agents_on_sites_top_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOM365AgentInsightsM365AgentsOnSitesDetails]]:
        """GetM365AgentsOnSitesTopDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenant.administration.spom365agentinsightsm365agentsonsitesdetails import (
            SPOM365AgentInsightsM365AgentsOnSitesDetails,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOM365AgentInsightsM365AgentsOnSitesDetails]())
        qry = ServiceOperationQuery(
            self,
            "GetM365AgentsOnSitesTopDetails",
            None,
            {"reportId": report_id, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_site_distributions_top_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOM365AgentInsightsSiteDistributionDetails]]:
        """GetSiteDistributionsTopDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenant.administration.spom365agentinsightssitedistributiondetails import (
            SPOM365AgentInsightsSiteDistributionDetails,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOM365AgentInsightsSiteDistributionDetails]())
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

    def get_top20_agents_top_details(
        self, report_id: UUID, is_full_details: bool
    ) -> ClientResult[ClientValueCollection[SPOM365AgentInsightsTop20AgentsDetails]]:
        """GetTop20AgentsTopDetails operation.

        Args:
            report_id (UUID):
                reportId parameter
            is_full_details (bool):
                isFullDetails parameter
        """
        from office365.sharepoint.tenantadministration.spom365_agent_insights_top20_agents_details import (
            SPOM365AgentInsightsTop20AgentsDetails,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOM365AgentInsightsTop20AgentsDetails]())
        qry = ServiceOperationQuery(
            self,
            "GetTop20AgentsTopDetails",
            None,
            {"reportId": report_id, "isFullDetails": is_full_details},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
