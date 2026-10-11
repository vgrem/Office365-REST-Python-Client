from __future__ import annotations

from datetime import datetime

from office365.entity import Entity
from office365.onedrive.workbooks.functions.result import WorkbookFunctionResult
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookFunctions(Entity):
    """Used as a container for Microsoft Excel worksheet function"""

    def abs(self, number):
        """Returns the absolute value of a number. The absolute value of a number is the number without its sign

        Args:
            number (float): The real number of which you want the absolute value.
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "number": number,
        }
        qry = ServiceOperationQuery(self, "abs", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def accr_int(self, issue, first_interest, settlement, rate, par, frequency):
        """Returns the accrued interest for a security that pays periodic interest.

        Args:
            issue (any): The real number of which you want the absolute value.
            first_interest (any): The security's first interest date.
            settlement (any): The security's settlement date. The security settlement date is the date after the
              issue date when the security is traded to the buyer.
            rate (any): The security's annual coupon rate.
            par (any): The security's par value. If you omit par, ACCRINT uses $1,000.
            frequency (any): The number of coupon payments per year. For annual payments, frequency = 1;
              for semiannual, frequency = 2; for quarterly, frequency = 4.
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "issue": issue,
            "firstInterest": first_interest,
            "settlement": settlement,
            "rate": rate,
            "par": par,
            "frequency": frequency,
        }
        qry = ServiceOperationQuery(self, "accrInt", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def accr_int_m(self, issue, settlement, rate, par, basis):
        """Returns the accrued interest for a security that pays periodic interest.

        Args:
            issue (any): The real number of which you want the absolute value.
            settlement (any): The security's settlement date. The security settlement date is the date after the
              issue date when the security is traded to the buyer.
            rate (any): The security's annual coupon rate.
            par (any): The security's par value. If you omit par, ACCRINT uses $1,000.
            basis (any):
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "issue": issue,
            "settlement": settlement,
            "rate": rate,
            "par": par,
            "basis": basis,
        }
        qry = ServiceOperationQuery(self, "accrIntM", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def days(self, start_date: datetime, end_date: datetime) -> WorkbookFunctionResult:
        """Returns the number of days between two dates.

        Args:
            start_date (datetime.datetime): Two dates between which you want to know the number of days.
            end_date (datetime.datetime): Two dates between which you want to know the number of days.
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "startDate": start_date.isoformat() + "Z",
            "endDate": end_date.isoformat() + "Z",
        }
        qry = ServiceOperationQuery(self, "days", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def power(self, number, power):
        """Returns the result of a number raised to a power.

        Args:
            number (int): The base number.
            power (int): The exponent to which the base number is raised.
        """
        return_type = WorkbookFunctionResult(self.context)
        payload = {
            "number": number,
            "power": power,
        }
        qry = ServiceOperationQuery(self, "power", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookFunctions"
