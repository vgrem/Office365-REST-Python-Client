from office365.reports.report import Report
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


def create_report_query(report_root, report_name, period=None):
    """
    Construct Report query

    :param office365.reports.report_root.ReportRoot report_root: Report container
    :param str report_name: Report name
    :param str period: Specifies the length of time over which the report is aggregated.
        The supported values for {period_value} are: D7, D30, D90, and D180. These values follow the format
        Dn where n represents the number of days over which the report is aggregated. Required.
    """
    params = {
        "period": period,
    }
    return_type = ClientResult(report_root.context, Report())
    qry = ServiceOperationQuery(report_root, report_name, params, None, None, return_type)

    def _construct_query(request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Get

    report_root.context.before_execute(_construct_query)
    return qry
