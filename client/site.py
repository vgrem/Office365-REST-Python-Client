from client.runtime.client_object import ClientObject
from web import Web


class Site(ClientObject):
    """Site client object"""

    def __init__(self, context):
        super(Site, self).__init__(context, "site")

    @property
    def root_web(self):
        """Get root web"""
        if self.is_property_available('RootWeb'):
            return self.properties['RootWeb']
        else:
            return Web(self.context)
