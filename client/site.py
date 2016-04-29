from client_object import ClientObject
from web import Web


class Site(ClientObject):
    """Site client object"""

    @property
    def root_web(self):
        """Get root web"""
        if self.is_property_available('RootWeb'):
            return self.properties['RootWeb']
        else:
            return Web(self.context)
