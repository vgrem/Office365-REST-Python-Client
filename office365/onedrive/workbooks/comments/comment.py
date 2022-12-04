from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.comments.reply import WorkbookCommentReply
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookComment(Entity):
    """Represents a comment in workbook."""

    @property
    def replies(self):
        """"""
        return self.properties.get('replies',
                                   EntityCollection(self.context, WorkbookCommentReply,
                                                    ResourcePath("replies", self.resource_path)))
