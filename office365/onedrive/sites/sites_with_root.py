from office365.entity_collection import EntityCollection
from office365.onedrive.sites.site import Site
from office365.runtime.resource_path import ResourcePath


class SitesWithRoot(EntityCollection):
    """Sites container"""

    def __init__(self, context, resource_path):
        super(SitesWithRoot, self).__init__(context, Site, resource_path)

    @property
    def root(self):
        return self.properties.get('root',
                                   Site(self.context, ResourcePath("root", self.resource_path)))

