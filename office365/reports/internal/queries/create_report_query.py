from office365.reports.report import Report
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery


def create_report_query(report_root, report_name, period=None):
    """
    Construct Report query

    :param office365.reports.root.ReportRoot report_root: Report container
    :param str report_name: Report name
    :param str period: Specifies the length of time over which the report is aggregated.
        The supported values for {period_value} are: D7, D30, D90, and D180. These values follow the format
        Dn where n represents the number of days over which the report is aggregated. Required.
    """
    params = {
        "period": period,
    }
    return_type = ClientResult(report_root.context, Report())
    return FunctionQuery(report_root, report_name, params, return_type)
