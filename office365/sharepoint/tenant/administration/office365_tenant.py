from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.users_results import GetExternalUsersResults, RemoveExternalUsersResults
from office365.sharepoint.tenant.administration.theme_properties import ThemeProperties


class Office365Tenant(BaseEntity):

    def __init__(self, context):
        super(Office365Tenant, self).__init__(
            context,
            ResourcePath("Microsoft.Online.SharePoint.TenantManagement.Office365Tenant")
        )

    def get_external_users(self, position=0, page_size=10, _filter=None, sort_order=0):
        """

        :param int position:
        :param int page_size:
        :param str _filter:
        :param int sort_order:
        """
        return_type = GetExternalUsersResults(self.context)
        payload = {
            "position": position,
            "pageSize": page_size,
            "filter": _filter,
            "sortOrder": sort_order
        }
        qry = ServiceOperationQuery(self, "GetExternalUsers", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_external_users(self, unique_ids=None):
        """

        :param list[str] unique_ids:
        """
        payload = {
            "uniqueIds": unique_ids,
        }
        return_type = RemoveExternalUsersResults(self.context)
        qry = ServiceOperationQuery(self, "RemoveExternalUsers", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_tenant_themes(self):
        """
        Get all themes from tenant
        """
        return_type = ClientObjectCollection(self.context, ThemeProperties)
        qry = ServiceOperationQuery(self, "GetAllTenantThemes", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_tenant_theme(self, name, theme_json):
        """
        Adds a new theme to a tenant.

        :param str name:
        :param str theme_json:
        """
        return_type = ClientResult(self.context)
        payload = {
            "name": name,
            "themeJson": theme_json,
        }
        qry = ServiceOperationQuery(self, "AddTenantTheme", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_tenant_theme(self, name):
        """
        Removes a theme from tenant

        :type name: str
        """
        payload = {
            "name": name,
        }
        qry = ServiceOperationQuery(self, "DeleteTenantTheme", None, payload)
        self.context.add_query(qry)
        return self
