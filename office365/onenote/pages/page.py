from office365.entity_collection import EntityCollection
from office365.onenote.entity_schema_object_model import OnenoteEntitySchemaObjectModel
from office365.onenote.internal.multipart_page_query import OneNotePageCreateQuery
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.pages.page_links import PageLinks
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


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


class OnenotePage(OnenoteEntitySchemaObjectModel):
    """A page in a OneNote notebook."""

    def get_content(self):
        """Download the page's HTML content. """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "content", None, None, None, result)

        def _construct_query(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get

        self.context.before_execute(_construct_query)
        self.context.add_query(qry)
        return result

    @property
    def content_url(self):
        """The URL for the page's HTML content. Read-only.

        :rtype: str or None
        """
        return self.properties.get("contentUrl", None)

    @property
    def links(self):
        """Links for opening the page. The oneNoteClientURL link opens the page in the OneNote native client
        if it 's installed. The oneNoteWebUrl link opens the page in OneNote on the web. Read-only.

        """
        return self.properties.get("links", PageLinks())

    @property
    def title(self):
        """The title of the page.
        """
        return self.properties.get("title", None)

    @property
    def user_tags(self):
        """Links for opening the page. The oneNoteClientURL link opens the page in the OneNote native client
        if it 's installed. The oneNoteWebUrl link opens the page in OneNote on the web. Read-only.

        """
        return self.properties.get("userTags", ClientValueCollection(str))

    @property
    def parent_notebook(self):
        """The notebook that contains the page. Read-only.

        :rtype: Notebook
        """
        return self.get_property('parentNotebook',
                                 Notebook(self.context, ResourcePath("parentNotebook", self.resource_path)))

    @property
    def parent_section(self):
        """The section that contains the page. Read-only.

        :rtype: OnenoteSection
        """
        return self.get_property('parentSection',
                                 OnenoteSection(self.context, ResourcePath("parentSection", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "userTags": self.user_tags,
                "parentSection": self.parent_section,
                "parentNotebook": self.parent_notebook
            }
            default_value = property_mapping.get(name, None)
        return super(OnenotePage, self).get_property(name, default_value)
