from office365.sharepoint.publishing.pages.page import SitePage


class CampaignPublication(SitePage):

    @property
    def entity_type_name(self):
        return "SP.Publishing.CampaignPublication"
