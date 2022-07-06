from office365.entity_collection import EntityCollection
from office365.onenote.internal.multipart_page_query import OneNotePageCreateQuery
from office365.onenote.pages.page import OnenotePage


class OnenotePageCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(OnenotePageCollection, self).__init__(context, OnenotePage, resource_path)

    def add(self, presentation_file, attachment_files=None):
        """
        :rtype: OnenotePage
        """
        qry = OneNotePageCreateQuery(self, presentation_file, attachment_files)
        self.context.add_query(qry)
        return qry.return_type
