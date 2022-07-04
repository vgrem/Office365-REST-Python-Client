from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class TenantSettings(BaseEntity):
    """Specifies the tenant properties."""

    def clear_corporate_catalog(self):
        qry = ServiceOperationQuery(self, "ClearCorporateCatalog", None, None, None, None)
        self.context.add_query(qry)
        return self

    def set_corporate_catalog(self, url):
        """
        :param str url:
        """
        payload = {"url": url}
        qry = ServiceOperationQuery(self, "SetCorporateCatalog", None, payload, None, None)
        self.context.add_query(qry)
        return self

    @property
    def corporate_catalog_url(self):
        """Specifies the URL of the corporate catalog site collection.

        :rtype: str or None
        """
        return self.properties.get('CorporateCatalogUrl', None)

    @staticmethod
    def current(context):
        """
        Specifies the current instance for the SP.TenantSettings.

        :type context: office365.sharepoint.client_context.ClientContext
        """
        return TenantSettings(context, ResourcePath("SP.TenantSettings.Current"))
