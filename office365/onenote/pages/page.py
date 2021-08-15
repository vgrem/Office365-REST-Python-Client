from office365.onenote.entity_schema_object_model import OnenoteEntitySchemaObjectModel
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.resource_path import ResourcePath


class OnenotePage(OnenoteEntitySchemaObjectModel):
    """A page in a OneNote notebook."""

    @property
    def content_url(self):
        """The URL for the page's HTML content. Read-only.

        :rtype: str or None
        """
        return self.properties.get("contentUrl", None)

    @property
    def parent_notebook(self):
        """The notebook that contains the page. Read-only."""
        return self.get_property('parentNotebook',
                                 Notebook(self.context, ResourcePath("parentNotebook", self.resource_path)))

    @property
    def parent_section(self):
        """The section that contains the page. Read-only."""
        return self.get_property('parentSection',
                                 OnenoteSection(self.context, ResourcePath("parentSection", self.resource_path)))
