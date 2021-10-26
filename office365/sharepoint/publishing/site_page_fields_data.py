from office365.runtime.client_value import ClientValue


class SitePageFieldsData(ClientValue):

    def __init__(self, title=None, banner_image_url=None, canvas_content=None, canvas_json=None, topic_header=None):
        """
        Represents Site Page metadata for use in page authoring operations.

        :param str title: the Page title
        :param str banner_image_url: the preview image Url for the current Site Page.
        :param str canvas_content: CanvasContent1 for the current Site Page.
        :param str canvas_json: CanvasContent1 of the current Site Page based on a stringified JSON object structure.
        """
        super(SitePageFieldsData, self).__init__()
        self.BannerImageUrl = banner_image_url
        self.CanvasContent1 = canvas_content
        self.CanvasJson1 = canvas_json
        self.Title = title
        self.TopicHeader = topic_header

    @property
    def entity_type_name(self):
        return "SP.Publishing.SitePageFieldsData"
