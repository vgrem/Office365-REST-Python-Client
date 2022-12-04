from office365.entity import Entity
from office365.onedrive.workbooks.functions.result import WorkbookFunctionResult
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookFunctions(Entity):
    """Used as a container for Microsoft Excel worksheet function"""

    def abs(self, number):
        """"""
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "number": number,
        }
        qry = ServiceOperationQuery(self, "abs", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def days(self, start_date, end_date):
        """Returns the number of days between two dates.

        :param datetime start_date:
        :param datetime end_date:
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "startDate": start_date,
            "endDate": end_date
        }
        qry = ServiceOperationQuery(self, "days", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
