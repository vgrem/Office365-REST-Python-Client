from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path_entry import ResourcePathEntry
from web import Web


class Site(ClientObject):
    """Site client object"""

    def __init__(self, context):
        super(Site, self).__init__(context, ResourcePathEntry(context, None, "Site"))

    @property
    def root_web(self):
        """Get root web"""
        if self.is_property_available('RootWeb'):
            return self.properties['RootWeb']
        else:
            return Web(self.context, ResourcePathEntry(self.context, self.resource_path, "RootWeb"))
