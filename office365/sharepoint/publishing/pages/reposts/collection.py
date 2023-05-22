from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.pages.reposts.repost import RepostPage


class RepostPageCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(RepostPageCollection, self).__init__(context, RepostPage, resource_path)
