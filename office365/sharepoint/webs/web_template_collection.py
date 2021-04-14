from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.webs.web_template import WebTemplate


class WebTemplateCollection(BaseEntityCollection):
    """Specifies a collection of site templates."""

    def __init__(self, context, resource_path=None, parent=None):
        super(WebTemplateCollection, self).__init__(context, WebTemplate, resource_path, parent)

    def get_by_name(self, name):
        """Returns the SP.WebTemplate (section 3.2.5.151) specified by its name.<162>

        :param str name: The name of the SP.WebTemplate that is returned.

        """
        return WebTemplate(self.context,
                           ResourcePathServiceOperation("getByName", [f"{name}"], self.resource_path))
