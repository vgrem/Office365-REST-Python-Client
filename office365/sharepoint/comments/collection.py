from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.comments.comment import Comment


class CommentCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(CommentCollection, self).__init__(context, Comment, resource_path)

    def delete_all(self):
        """Deletes all the comments."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "DeleteAll", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type
