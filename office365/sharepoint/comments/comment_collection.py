from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.comments.comment import Comment


class CommentCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(CommentCollection, self).__init__(context, Comment, resource_path)
