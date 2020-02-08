from office365.onedrive.site import Site
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath


class SiteCollection(ClientObjectCollection):
    """Drive site's collection"""

    def __init__(self, context, resource_path=None):
        super(SiteCollection, self).__init__(context, Site, resource_path)

    @property
    def root(self):
        """If present, indicates that this is a root site collection in SharePoint."""
        if self.is_property_available('root'):
            return self.properties['root']
        else:
            return Site(self.context, ResourcePath("root", self.resourcePath))
