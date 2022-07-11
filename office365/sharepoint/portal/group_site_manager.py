from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.portal.group_creation_params import GroupCreationInformation
from office365.sharepoint.portal.group_site_info import GroupSiteInfo


class GroupSiteManager(ClientObject):

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("GroupSiteManager")
        super(GroupSiteManager, self).__init__(context, resource_path)

    def create_group_for_site(self, display_name, alias, is_public=None, optional_params=None):
        """
        Create a modern site

        :param str display_name:
        :param str alias:
        :param bool or None is_public:
        :param office365.sharepoint.portal.group_creation_params.GroupCreationParams or None optional_params:
        """
        payload = {
            "displayName": display_name,
            "alias": alias,
            "isPublic": is_public,
            "optionalParams": optional_params
        }
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "CreateGroupForSite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_group_ex(self, display_name, alias, is_public, optional_params=None):
        """
        Create a modern site

        :param str display_name:
        :param str alias:
        :param bool is_public:
        :param office365.sharepoint.portal.group_creation_params.GroupCreationParams or None optional_params:
        """
        payload = GroupCreationInformation(display_name, alias, is_public, optional_params)
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "CreateGroupEx", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

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
        return self

    def get_status(self, group_id):
        """Get the status of a SharePoint site

        :type group_id: str
        """
        result = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "GetSiteStatus", None, {'groupId': group_id}, None, result)
        self.context.add_query(qry)

        def _construct_status_request(request):
            request.method = HttpMethod.Get
            request.url += "?groupId='{0}'".format(group_id)

        self.context.before_execute(_construct_status_request)
        return result

    def get_current_user_joined_teams(self, get_logo_data=False, force_cache_update=False):
        """
        Get the teams in Microsoft Teams that the current user is a direct member of.

        :type get_logo_data: bool
        :type force_cache_update: bool
        """
        result = ClientResult(self.context)
        payload = {
            "getLogoData": get_logo_data,
            "forceCacheUpdate": force_cache_update
        }
        qry = ServiceOperationQuery(self, "GetCurrentUserJoinedTeams", None, payload, None, result)
        self.context.add_query(qry)
        return result
