from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class SPOWebAppServicePrincipal(BaseEntity):

    def __init__(self, context):
        stat_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal")
        super(SPOWebAppServicePrincipal, self).__init__(context, stat_path)


    def update_spfx_client_secret(self, secret_value):
        """
        :param str secret_value:
        """
        payload = {"secretValue": secret_value}
        qry = ServiceOperationQuery(self, "UpdateSpfxClientSecret", None, payload)
        self.context.add_query(qry)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal"
