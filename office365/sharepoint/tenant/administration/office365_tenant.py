from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.theme_properties import ThemeProperties


class Office365Tenant(BaseEntity):

    def __init__(self, context):
        super(Office365Tenant, self).__init__(
            context,
            ResourcePath("Microsoft.Online.SharePoint.TenantManagement.Office365Tenant")
        )

    @staticmethod
    def get_all_tenant_themes(context):
        """
        Removes a theme from tenant

        :type context: office365.sharepoint.client_context.ClientContext
        """
        tenant = Office365Tenant(context)
        return_type = ClientObjectCollection(context, ThemeProperties)
        qry = ServiceOperationQuery(tenant, "GetAllTenantThemes", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return tenant

    @staticmethod
    def delete_tenant_theme(context, name):
        """
        Removes a theme from tenant

        :type context: office365.sharepoint.client_context.ClientContext
        :type name: str
        """
        payload = {
            "name": name,
        }
        tenant = Office365Tenant(context)
        qry = ServiceOperationQuery(tenant, "DeleteTenantTheme", None, payload)
        qry.static = True
        context.add_query(qry)
        return tenant
