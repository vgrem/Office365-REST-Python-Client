from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class CorporateCatalogAppMetadata(BaseEntity):
    """App metadata for apps stored in the corporate catalog."""

    def install(self):
        """This method allows an app which is already deployed to be installed on a web."""
        qry = ServiceOperationQuery(self, "Install")
        self.context.add_query(qry)
        return self

    def uninstall(self):
        """This method uninstalls an app from a web."""
        qry = ServiceOperationQuery(self, "Uninstall")
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Marketplace.CorporateCuratedGallery.CorporateCatalogAppMetadata"
