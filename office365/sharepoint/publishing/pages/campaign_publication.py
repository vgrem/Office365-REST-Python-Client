from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.publishing.highlights_info import HighlightsInfo
from office365.sharepoint.publishing.pages.page import SitePage


class CampaignPublication(SitePage):

    def get_highlights_info(self):
        """
        """
        return_type = HighlightsInfo(self.context)
        qry = ServiceOperationQuery(self, "GetHighlightsInfo", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Publishing.CampaignPublication"
