from office365.sharepoint.search.reports.base import ReportBase


class ReportTopQueries(ReportBase):

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.ReportTopQueries"
