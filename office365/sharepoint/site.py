from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.web import Web


class Site(ClientObject):
    """Site client object"""

    def __init__(self, context):
        super(Site, self).__init__(context, ResourcePath("Site", None))

    @property
    def rootWeb(self):
        """Get root web"""
        if self.is_property_available('RootWeb'):
            return self.properties['RootWeb']
        else:
            return Web(self.context, ResourcePath("RootWeb", self.resourcePath))
