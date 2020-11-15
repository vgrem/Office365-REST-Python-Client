from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.publishing.topic_site_page import TopicSitePage


class TopicPageCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TopicPageCollection, self).__init__(context, TopicSitePage, resource_path)
