from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.comments.comment import Comment


class CommentCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(CommentCollection, self).__init__(context, Comment, resource_path)
