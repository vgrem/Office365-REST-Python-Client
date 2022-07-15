from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.query.configuration import QueryConfiguration
from office365.sharepoint.search.reports.base import ReportBase


class SearchSetting(BaseEntity):
    """This object provides the REST operations defined under search settings."""

    def __init__(self, context):
        super(SearchSetting, self).__init__(context, ResourcePath("Microsoft.Office.Server.Search.REST.SearchSetting"))

    def get_query_configuration(self, call_local_search_farms_only=True):
        """
        This REST operation gets the query configuration. See section 3.1.5.18.2.1.6.

        :param bool call_local_search_farms_only: This is a flag that indicates to only call the local search farm.
        """
        result = ClientResult(self.context, QueryConfiguration())
        payload = {
            "callLocalSearchFarmsOnly": call_local_search_farms_only
        }
        qry = ServiceOperationQuery(self, "getqueryconfiguration", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def export_search_reports(self, tenant_id, report_type=None, interval=None,
                              start_date=None, end_date=None, site_collection_id=None):
        """
        :param str tenant_id:
        :param str report_type:
        :param str interval:
        :param str start_date:
        :param str end_date:
        :param str site_collection_id:
        """
        result = ClientResult(self.context, ReportBase())
        payload = {
            "TenantId": tenant_id,
            "ReportType": report_type,
            "Interval": interval,
            "StartDate": start_date,
            "EndDate": end_date,
            "SiteCollectionId": site_collection_id
        }
        qry = ServiceOperationQuery(self, "ExportSearchReports", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def ping_admin_endpoint(self):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "PingAdminEndpoint", None, None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchSetting"
