from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class SPHSite(BaseEntity):

    def __init__(self, context):
        """
        A home site represents a SharePoint communication site.
        It brings together news, events, embedded video and conversations, and other resources to deliver an engaging
        experience that reflects your organization's voice, priorities, and brand.
        It also allows your users to search for content (such as sites, news, and files) across your organization
        """
        super(SPHSite, self).__init__(context, ResourcePath("SP.SPHSite"))

    @staticmethod
    def is_valid_home_site(context, site_url, return_value=None):
        """
        Determines whether a site is landing site for your intranet.

        :param ClientResult return_value:
        :param office365.sharepoint.client_context.ClientContext context:
        :param str site_url:
        :return:
        """

        if return_value is None:
            return_value = ClientResult(context)
        sph = SPHSite(context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(sph, "IsValidHomeSite", params, None, None, return_value)
        qry.static = True
        context.add_query(qry)
        return return_value

    @staticmethod
    def set_as_home_site(context, site_url, return_value=None):
        """
        Sets a site as a landing site for your intranet.

        :param ClientResult return_value:
        :param office365.sharepoint.client_context.ClientContext context:
        :param str site_url:
        """

        if return_value is None:
            return_value = ClientResult(context)
        sph = SPHSite(context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(sph, "SetSPHSite", params, None, None, return_value)
        qry.static = True
        context.add_query(qry)
        return return_value
