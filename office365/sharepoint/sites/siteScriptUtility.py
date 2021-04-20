from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.siteDesignPrincipal import SiteDesignPrincipalCollection


class SiteScriptUtility(BaseEntity):

    def __init__(self, context):
        super().__init__(context,
                         ResourcePath("Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteScriptUtility"))

    @staticmethod
    def get_site_design_rights(context, _id):
        """

        :type _id: str
        :param office365.sharepoint.client_context.ClientContext context: client context

        """
        return_type = SiteDesignPrincipalCollection(context)
        utility = SiteScriptUtility(context)
        qry = ServiceOperationQuery(utility, "GetSiteDesignRights", [_id], None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_list_design(context):
        pass
