from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.sharepoint.entity import Entity
from typing_extensions import Self

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.audit.datacollectionresponse import (
        SPAuditDataCollectionResponse,
    )
    from office365.sharepoint.tenant.administration.data_governance_insight_query_parameters import (
        SPDataGovernanceInsightQueryParameters,
    )
    from office365.sharepoint.tenant.administration.datagovernance.insight_metadata import (
        SPDataGovernanceInsightMetadata,
    )
    from office365.sharepoint.tenant.administration.sp_data_governance_insight_create_parameters import (
        SPDataGovernanceInsightCreateParameters,
    )
    from office365.sharepoint.tenant.administration.sp_data_governance_opt_in_parameters import (
        SPDataGovernanceOptInParameters,
    )
    from office365.sharepoint.tenant.administration.spdatagovernanceinsightresponse import (
        SPDataGovernanceInsightResponse,
    )


class SPDataGovernanceInsightRestApiClient(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPDataGovernanceInsightRestApiClient"

    def create_data_access_governance_report(
        self,
        report_entity: int,
        workload: int,
        report_type: int,
        file_sensitivity_label_name: str,
        file_sensitivity_label_guid: str,
        name: str,
        template: list[int],
        privacy: str,
        site_sensitivity_label_guid: list[UUID],
        count_of_users_more_than: int,
    ) -> ClientResult[SPDataGovernanceInsightMetadata]:
        """CreateDataAccessGovernanceReport operation.

        Args:
            report_entity (int):
                reportEntity parameter
            workload (int):
                workload parameter
            report_type (int):
                reportType parameter
            file_sensitivity_label_name (str):
                fileSensitivityLabelName parameter
            file_sensitivity_label_guid (str):
                fileSensitivityLabelGUID parameter
            name (str):
                name parameter
            template (list[int]):
                template parameter
            privacy (str):
                privacy parameter
            site_sensitivity_label_guid (list[UUID]):
                siteSensitivityLabelGUID parameter
            count_of_users_more_than (int):
                countOfUsersMoreThan parameter
        """
        from office365.sharepoint.tenant.administration.datagovernance.insight_metadata import (
            SPDataGovernanceInsightMetadata,
        )

        return_type = ClientResult(self.context, SPDataGovernanceInsightMetadata())
        qry = ServiceOperationQuery(
            self,
            "CreateDataAccessGovernanceReport",
            None,
            {
                "reportEntity": report_entity,
                "workload": workload,
                "reportType": report_type,
                "fileSensitivityLabelName": file_sensitivity_label_name,
                "fileSensitivityLabelGUID": file_sensitivity_label_guid,
                "name": name,
                "template": ClientValueCollection(int, template),
                "privacy": privacy,
                "siteSensitivityLabelGUID": GuidCollection(site_sensitivity_label_guid),
                "countOfUsersMoreThan": count_of_users_more_than,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_data_access_governance_report_v2(
        self,
        report_entity: int,
        workload: int,
        report_type: int,
        file_sensitivity_label_name: str,
        file_sensitivity_label_guid: str,
        name: str,
        template: list[int],
        privacy: str,
        site_sensitivity_label_guid: list[UUID],
        count_of_users_more_than: int,
        user_id_list: list[UUID],
    ) -> ClientResult[SPDataGovernanceInsightMetadata]:
        """CreateDataAccessGovernanceReportV2 operation.

        Args:
            report_entity (int):
                reportEntity parameter
            workload (int):
                workload parameter
            report_type (int):
                reportType parameter
            file_sensitivity_label_name (str):
                fileSensitivityLabelName parameter
            file_sensitivity_label_guid (str):
                fileSensitivityLabelGUID parameter
            name (str):
                name parameter
            template (list[int]):
                template parameter
            privacy (str):
                privacy parameter
            site_sensitivity_label_guid (list[UUID]):
                siteSensitivityLabelGUID parameter
            count_of_users_more_than (int):
                countOfUsersMoreThan parameter
            user_id_list (list[UUID]):
                userIDList parameter
        """
        from office365.sharepoint.tenant.administration.datagovernance.insight_metadata import (
            SPDataGovernanceInsightMetadata,
        )

        return_type = ClientResult(self.context, SPDataGovernanceInsightMetadata())
        qry = ServiceOperationQuery(
            self,
            "CreateDataAccessGovernanceReportV2",
            None,
            {
                "reportEntity": report_entity,
                "workload": workload,
                "reportType": report_type,
                "fileSensitivityLabelName": file_sensitivity_label_name,
                "fileSensitivityLabelGUID": file_sensitivity_label_guid,
                "name": name,
                "template": ClientValueCollection(int, template),
                "privacy": privacy,
                "siteSensitivityLabelGUID": GuidCollection(site_sensitivity_label_guid),
                "countOfUsersMoreThan": count_of_users_more_than,
                "userIDList": GuidCollection(user_id_list),
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_data_access_governance_report_v3(
        self,
        report_entity: int,
        workload: int,
        report_type: int,
        file_sensitivity_label_name: str,
        file_sensitivity_label_guid: str,
        name: str,
        template: list[int],
        privacy: str,
        site_sensitivity_label_guid: list[UUID],
        count_of_users_more_than: int,
        user_email_list: list[str],
    ) -> ClientResult[SPDataGovernanceInsightMetadata]:
        """CreateDataAccessGovernanceReportV3 operation.

        Args:
            report_entity (int):
                reportEntity parameter
            workload (int):
                workload parameter
            report_type (int):
                reportType parameter
            file_sensitivity_label_name (str):
                fileSensitivityLabelName parameter
            file_sensitivity_label_guid (str):
                fileSensitivityLabelGUID parameter
            name (str):
                name parameter
            template (list[int]):
                template parameter
            privacy (str):
                privacy parameter
            site_sensitivity_label_guid (list[UUID]):
                siteSensitivityLabelGUID parameter
            count_of_users_more_than (int):
                countOfUsersMoreThan parameter
            user_email_list (list[str]):
                userEmailList parameter
        """
        from office365.sharepoint.tenant.administration.datagovernance.insight_metadata import (
            SPDataGovernanceInsightMetadata,
        )

        return_type = ClientResult(self.context, SPDataGovernanceInsightMetadata())
        qry = ServiceOperationQuery(
            self,
            "CreateDataAccessGovernanceReportV3",
            None,
            {
                "reportEntity": report_entity,
                "workload": workload,
                "reportType": report_type,
                "fileSensitivityLabelName": file_sensitivity_label_name,
                "fileSensitivityLabelGUID": file_sensitivity_label_guid,
                "name": name,
                "template": ClientValueCollection(int, template),
                "privacy": privacy,
                "siteSensitivityLabelGUID": GuidCollection(site_sensitivity_label_guid),
                "countOfUsersMoreThan": count_of_users_more_than,
                "userEmailList": StringCollection(user_email_list),
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_data_access_governance_report_v4(
        self, request: SPDataGovernanceInsightCreateParameters
    ) -> ClientResult[SPDataGovernanceInsightMetadata]:
        """CreateDataAccessGovernanceReportV4 operation.

        Args:
            request (SPDataGovernanceInsightCreateParameters):
                request parameter
        """
        from office365.sharepoint.tenant.administration.datagovernance.insight_metadata import (
            SPDataGovernanceInsightMetadata,
        )

        return_type = ClientResult(self.context, SPDataGovernanceInsightMetadata())
        qry = ServiceOperationQuery(
            self, "CreateDataAccessGovernanceReportV4", None, {"request": request}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def export_spo_data_access_governance_insight(self, report_id: UUID) -> ClientResult[str]:
        """ExportSPODataAccessGovernanceInsight operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "ExportSPODataAccessGovernanceInsight", None, {"reportId": report_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def export_spo_data_access_governance_insight_v2(self, report_id: UUID) -> ClientResult[str]:
        """ExportSPODataAccessGovernanceInsightV2 operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "ExportSPODataAccessGovernanceInsightV2", None, {"reportId": report_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def export_spo_data_access_governance_insight_v3(self, report_id: UUID) -> ClientResult[str]:
        """ExportSPODataAccessGovernanceInsightV3 operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "ExportSPODataAccessGovernanceInsightV3", None, {"reportId": report_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_audit_data_collection_for_all_reports(
        self,
    ) -> ClientResult[ClientValueCollection[SPAuditDataCollectionResponse]]:
        """GetSPOAuditDataCollectionForAllReports operation."""
        from office365.sharepoint.tenant.administration.audit.datacollectionresponse import (
            SPAuditDataCollectionResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPAuditDataCollectionResponse]())
        qry = ServiceOperationQuery(self, "GetSPOAuditDataCollectionForAllReports", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_audit_data_collection_for_report(
        self, report_entity: int
    ) -> ClientResult[ClientValueCollection[SPAuditDataCollectionResponse]]:
        """GetSPOAuditDataCollectionForReport operation.

        Args:
            report_entity (int):
                reportEntity parameter
        """
        from office365.sharepoint.tenant.administration.audit.datacollectionresponse import (
            SPAuditDataCollectionResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPAuditDataCollectionResponse]())
        qry = ServiceOperationQuery(
            self, "GetSPOAuditDataCollectionForReport", None, {"reportEntity": report_entity}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_data_access_governance_insight(
        self, report_entity: int, work_load: int
    ) -> ClientResult[ClientValueCollection[SPDataGovernanceInsightResponse]]:
        """GetSPODataAccessGovernanceInsight operation.

        Args:
            report_entity (int):
                reportEntity parameter
            work_load (int):
                workLoad parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernanceinsightresponse import (
            SPDataGovernanceInsightResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPDataGovernanceInsightResponse]())
        qry = ServiceOperationQuery(
            self,
            "GetSPODataAccessGovernanceInsight",
            None,
            {"reportEntity": report_entity, "workLoad": work_load},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_data_access_governance_insight_by_id(
        self, report_id: UUID
    ) -> ClientResult[SPDataGovernanceInsightResponse]:
        """GetSPODataAccessGovernanceInsightById operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernanceinsightresponse import (
            SPDataGovernanceInsightResponse,
        )

        return_type = ClientResult(self.context, SPDataGovernanceInsightResponse())
        qry = ServiceOperationQuery(
            self, "GetSPODataAccessGovernanceInsightById", None, {"reportId": report_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_data_access_governance_insight_v2(
        self, report_entity: int
    ) -> ClientResult[ClientValueCollection[SPDataGovernanceInsightResponse]]:
        """GetSPODataAccessGovernanceInsightV2 operation.

        Args:
            report_entity (int):
                reportEntity parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernanceinsightresponse import (
            SPDataGovernanceInsightResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPDataGovernanceInsightResponse]())
        qry = ServiceOperationQuery(
            self, "GetSPODataAccessGovernanceInsightV2", None, {"reportEntity": report_entity}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_data_access_governance_insight_v3(
        self, request: SPDataGovernanceInsightQueryParameters
    ) -> ClientResult[ClientValueCollection[SPDataGovernanceInsightResponse]]:
        """GetSPODataAccessGovernanceInsightV3 operation.

        Args:
            request (SPDataGovernanceInsightQueryParameters):
                request parameter
        """
        from office365.sharepoint.tenant.administration.spdatagovernanceinsightresponse import (
            SPDataGovernanceInsightResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPDataGovernanceInsightResponse]())
        qry = ServiceOperationQuery(
            self, "GetSPODataAccessGovernanceInsightV3", None, {"request": request}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def remove_data_access_governance_report(self, report_id: UUID) -> Self:
        """RemoveDataAccessGovernanceReport operation.

        Args:
            report_id (UUID):
                reportId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveDataAccessGovernanceReport", None, {"reportId": report_id}, None, None)
        self.context.add_query(qry)
        return self

    def set_opt_in_status_for_reports(
        self, report_entity: int, opt_in_status: bool
    ) -> ClientResult[SPAuditDataCollectionResponse]:
        """SetOptInStatusForReports operation.

        Args:
            report_entity (int):
                reportEntity parameter
            opt_in_status (bool):
                optInStatus parameter
        """
        from office365.sharepoint.tenant.administration.audit.datacollectionresponse import (
            SPAuditDataCollectionResponse,
        )

        return_type = ClientResult(self.context, SPAuditDataCollectionResponse())
        qry = ServiceOperationQuery(
            self,
            "SetOptInStatusForReports",
            None,
            {"reportEntity": report_entity, "optInStatus": opt_in_status},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_opt_in_status_for_reports_v2(
        self, request: SPDataGovernanceOptInParameters
    ) -> ClientResult[SPAuditDataCollectionResponse]:
        """SetOptInStatusForReportsV2 operation.

        Args:
            request (SPDataGovernanceOptInParameters):
                request parameter
        """
        from office365.sharepoint.tenant.administration.audit.datacollectionresponse import (
            SPAuditDataCollectionResponse,
        )

        return_type = ClientResult(self.context, SPAuditDataCollectionResponse())
        qry = ServiceOperationQuery(self, "SetOptInStatusForReportsV2", None, {"request": request}, None, return_type)
        self.context.add_query(qry)
        return return_type
