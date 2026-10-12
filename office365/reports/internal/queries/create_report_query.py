from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.reports.report_result import ReportResult
from office365.runtime.queries.function import FunctionQuery

if TYPE_CHECKING:
    from office365.reports.root import ReportRoot


def create_report_query(
    report_root: ReportRoot,
    report_name: str,
    period: Optional[str] = None,
) -> ReportResult:
    """Create, register, and return a report query result.

    Args:
        report_root (ReportRoot): Report container
        report_name (str): Report name
        period (str): Specifies the length of time over which the report is aggregated. The supported values for
          {period_value} are: D7, D30, D90, and D180. These values follow the format Dn where n represents the number
          of days over which the report is aggregated. Required.
    """
    return_type = ReportResult(report_root.context)
    qry = FunctionQuery(report_root, report_name, {"period": period}, return_type)
    report_root.context.add_query(qry)
    return return_type
