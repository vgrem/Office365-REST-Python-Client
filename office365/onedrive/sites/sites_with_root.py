from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.root import RootPath
from office365.onedrive.internal.paths.site import SitePath
from office365.onedrive.sites.site import Site
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery


class SitesWithRoot(EntityCollection):
    """Sites container"""

    def __init__(self, context, resource_path):
        super(SitesWithRoot, self).__init__(context, Site, resource_path)

    def get_by_url(self, url):
        """Address Site resource by absolute url

        :param str url: Site absolute url
        """
        return_type = Site(self.context, SitePath(url, self.resource_path))
        qry = ReadEntityQuery(return_type)
        self.context.add_query(qry)
        return return_type

    def remove(self, sites):
        """
        :type sites: SitesWithRoot
        """
        return_type = SitesWithRoot(self.context, self.resource_path)
        payload = {
            "value": sites,
        }
        qry = ServiceOperationQuery(self, "remove", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def root(self):
        return self.properties.get('root', Site(self.context, RootPath(self.resource_path, ResourcePath("sites"))))
