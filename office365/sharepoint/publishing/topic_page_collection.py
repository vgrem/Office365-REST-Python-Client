from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.topic_site_page import TopicSitePage


class TopicPageCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(TopicPageCollection, self).__init__(context, TopicSitePage, resource_path)
