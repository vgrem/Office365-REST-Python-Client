from office365.runtime.client_object import ClientObject
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.portal.GroupSiteInfo import GroupSiteInfo


class GroupSiteManager(ClientObject):
    def __init__(self, context):
        super(GroupSiteManager, self).__init__(context, ResourcePath("GroupSiteManager"), None)

    def create_group_ex(self, display_name, alias, is_public, optional_params):
        """
        Create a modern site

        :param str display_name:
        :param str alias:
        :param bool is_public:
        :param list or None optional_params:
        :return: GroupSiteInfo
        """
        payload = {
            "displayName": display_name,
            "alias": alias,
            "isPublic": is_public,
            "optionalParams": optional_params
        }
        group_site_info = GroupSiteInfo()
        qry = ServiceOperationQuery(self, "CreateGroupEx", None, payload, None, group_site_info)
        self.context.add_query(qry)
        return group_site_info

    def delete(self, site_url):
        """
        Deletes a SharePoint Team site

        :type site_url: str
        """
        payload = {
            "siteUrl": site_url
        }
        qry = ServiceOperationQuery(self, "Delete", None, payload)
        self.context.add_query(qry)

    def get_status(self, group_id):
        """Get the status of a SharePoint site"""
        group_site_info = GroupSiteInfo()
        qry = ServiceOperationQuery(self, "GetSiteStatus", None, {'groupId': group_id}, None, group_site_info)
        self.context.add_query(qry)
        self.context.get_pending_request().beforeExecute += self._construct_status_request
        return group_site_info

    def _construct_status_request(self, request):
        query = self.context.get_pending_request().current_query
        request.method = HttpMethod.Get
        request.url += "?groupId='{0}'".format(query.parameter_type['groupId'])
        self.context.get_pending_request().beforeExecute -= self._construct_status_request
