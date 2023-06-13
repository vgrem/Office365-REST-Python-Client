from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.comments.reply import WorkbookCommentReply
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookComment(Entity):
    """Represents a comment in workbook."""

    @property
    def content(self):
        """The content of comment.
        :rtype: str or None
        """
        return self.properties.get('content', None)

    @property
    def content_type(self):
        """Indicates the type for the comment.
        :rtype: str or None
        """
        return self.properties.get('contentType', None)

    @property
    def replies(self):
        """"""
        return self.properties.get('replies',
                                   EntityCollection(self.context, WorkbookCommentReply,
                                                    ResourcePath("replies", self.resource_path)))
