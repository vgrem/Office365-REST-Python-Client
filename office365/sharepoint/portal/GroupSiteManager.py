from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.portal.GroupSiteInfo import GroupSiteInfo


def _construct_status_request(request, query):
    request.method = HttpMethod.Get
    request.url += "?groupId='{0}'".format(query.parameters['groupId'])


class GroupSiteManager(ClientObject):
    def __init__(self, context):
        super(GroupSiteManager, self).__init__(context, ResourcePath("GroupSiteManager"), None)

    def create_group_ex(self, display_name, alias, is_public, optional_params):
        """Create a modern site"""
        payload = {
            "displayName": display_name,
            "alias": alias,
            "isPublic": is_public,
            "optionalParams": optional_params
        }
        qry = ServiceOperationQuery(self, "CreateGroupEx", None, payload)
        group_site_info = GroupSiteInfo()
        self.context.add_query(qry, group_site_info)
        return group_site_info

    def delete(self, site_url):
        """Deletes a SharePoint Team site"""
        payload = {
            "siteUrl": site_url
        }
        qry = ServiceOperationQuery(self, "Delete", None, payload)
        self.context.add_query(qry)

    def get_status(self, group_id):
        """Get the status of a SharePoint site"""
        group_site_info = GroupSiteInfo()
        qry = ServiceOperationQuery(self, "GetSiteStatus", None, {'groupId': group_id})
        self.context.add_query(qry, group_site_info)
        self.context.pending_request.before_execute_request(_construct_status_request)
        return group_site_info
