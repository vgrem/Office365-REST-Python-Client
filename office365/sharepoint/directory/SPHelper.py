from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.directory.members_info import MembersInfo
from office365.sharepoint.directory.user import User


class SPHelper(BaseEntity):

    def __init__(self, context):
        super(SPHelper, self).__init__(context, ResourcePath("SP.Directory.SPHelper"))

    @staticmethod
    def is_member_of(context, principal_name, group_id, result=None):
        """
        :param str principal_name: User principal name
        :param str group_id: Group id
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param ClientResult or None result: Client result
        """
        helper = SPHelper(context)
        if result is None:
            result = ClientResult(context)
        payload = {
            "principalName": principal_name,
            "groupId": group_id
        }
        qry = ServiceOperationQuery(helper, "IsMemberOf", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def check_site_availability(context, site_url):
        """
        :param str site_url: Site Url
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        """
        helper = SPHelper(context)
        result = ClientResult(context)
        qry = ServiceOperationQuery(helper, "CheckSiteAvailability",
                                    None, {"siteUrl": site_url},
                                    None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_members_info(context, group_id, row_limit, result=None):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str group_id: User's login
        :param int row_limit: Result offset
        :param MembersInfo result: Result
        """
        helper = SPHelper(context)
        if result is None:
            result = MembersInfo(context)
        payload = {
            "groupId": group_id,
            "rowLimit": row_limit,
        }
        qry = ServiceOperationQuery(helper, "GetMembersInfo", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_my_groups(context, logon_name, offset, length, result=None):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str logon_name: User's login
        :param int offset: Result offset
        :param int length: Results count
        :param ClientResult result: Result
        """
        helper = SPHelper(context)
        if result is None:
            result = ClientResult(context)
        payload = {
            "logOnName": logon_name,
            "offset": offset,
            "len": length
        }
        qry = ServiceOperationQuery(helper, "GetMyGroups", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_members(context, group_id, return_type=None):
        """
        :param str group_id: Group identifier
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param BaseEntityCollection or None return_type: Returns members
        """
        if return_type is None:
            return_type = BaseEntityCollection(context, User)
        helper = SPHelper(context)
        qry = ServiceOperationQuery(helper, "GetMembers", [group_id], None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_owners(context, group_id, return_type=None):
        """
        :param str group_id: Group identifier
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param BaseEntityCollection or None return_type: Returns members
        """
        helper = SPHelper(context)
        if return_type is None:
            return_type = BaseEntityCollection(context, User)
        qry = ServiceOperationQuery(helper, "GetOwners", [group_id], None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Directory.SPHelper"
