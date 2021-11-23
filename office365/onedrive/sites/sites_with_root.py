from office365.entity_collection import EntityCollection
from office365.onedrive.sites.site import Site
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


class SitesWithRoot(EntityCollection):
    """Sites container"""

    def __init__(self, context, resource_path):
        super(SitesWithRoot, self).__init__(context, Site, resource_path)

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
        return self.properties.get('root',
                                   Site(self.context, ResourcePath("root", self.resource_path)))

