from office365.entity_collection import EntityCollection
from office365.onedrive.internal.root_resource_path import RootResourcePath
from office365.onedrive.site import Site


class SiteCollection(EntityCollection):
    """Drive site's collection"""

    def __init__(self, context, resource_path=None):
        super(SiteCollection, self).__init__(context, Site, resource_path)

    @property
    def root(self):
        """If present, indicates that this is a root site collection in SharePoint."""
        root_site = self.properties.get('root',
                                        Site(self.context, RootResourcePath(self.resource_path)))
        return root_site
