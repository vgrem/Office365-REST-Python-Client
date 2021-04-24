from office365.entity_collection import EntityCollection
from office365.onedrive.site import Site
from office365.runtime.resource_path import ResourcePath


class SiteCollection(EntityCollection):
    """Drive site's collection"""

    def __init__(self, context, resource_path=None):
        super(SiteCollection, self).__init__(context, Site, resource_path)

    @property
    def root(self):
        """If present, indicates that this is a root site collection in SharePoint."""
        return self.properties.get('root',
                                   Site(self.context, ResourcePath("root", self.resource_path)))
