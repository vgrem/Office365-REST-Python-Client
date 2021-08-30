from office365.entity import Entity
from office365.reports.internal.queries.create_report_query import create_report_query


class ReportRoot(Entity):
    """The resource that represents an instance of History Reports."""

    def get_email_activity_counts(self, period):
        """
        Enables you to understand the trends of email activity (like how many were sent, read, and received)
        in your organization.

        :param str period: Specifies the length of time over which the report is aggregated.
            The supported values for {period_value} are: D7, D30, D90, and D180. These values follow the format
            Dn where n represents the number of days over which the report is aggregated. Required.
        """

        qry = create_report_query(self, "getEmailActivityCounts", period)
        self.context.add_query(qry)
        return qry.return_type

    def get_email_activity_user_counts(self, period):
        """
        Enables you to understand trends on the number of unique users who are performing email activities
        like send, read, and receive.

        :param str period: Specifies the length of time over which the report is aggregated.
            The supported values for {period_value} are: D7, D30, D90, and D180. These values follow the format
            Dn where n represents the number of days over which the report is aggregated. Required.
        """
        qry = create_report_query(self, "getEmailActivityUserCounts", period)
        self.context.add_query(qry)
        return qry.return_type

    def get_office365_activations_user_counts(self):
        """
        Get the count of Microsoft 365 activations on desktops and devices.

        """
        qry = create_report_query(self, "getOffice365ActivationsUserCounts")
        self.context.add_query(qry)
        return qry.return_type

    def get_onedrive_activity_file_counts(self, period):
        """
        Get the number of unique, licensed users that performed file interactions against any OneDrive account.

        :param str period: Specifies the length of time over which the report is aggregated.
            The supported values for {period_value} are: D7, D30, D90, and D180. These values follow the format
            Dn where n represents the number of days over which the report is aggregated. Required.
        """
        qry = create_report_query(self, "getOneDriveActivityFileCounts", period)
        self.context.add_query(qry)
        return qry.return_type
