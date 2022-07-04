from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webparts.definition import WebPartDefinition


class WebPartDefinitionCollection(BaseEntityCollection):
    """Implements a collection of Web Part definition objects"""

    def __init__(self, context, resource_path=None):
        super(WebPartDefinitionCollection, self).__init__(context, WebPartDefinition, resource_path)
