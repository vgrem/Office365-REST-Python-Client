from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.files.file import File


class Utility(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.Utilities.Utility"))

    @staticmethod
    def get_current_user_email_addresses(context):
        """

        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(str)
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "GetCurrentUserEmailAddresses", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_user_permission_levels(context):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(ClientValueCollection(str))
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "GetUserPermissionLevels", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def search_principals_using_context_web(context, s_input, sources, scopes, maxCount, groupName=None):
        """
        :type s_input: str
        :type sources: int
        :type scopes: int
        :type maxCount: int
        :type groupName: str or None
        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(ClientValueCollection(str))
        utility = Utility(context)
        params = {
            "input": s_input,
            "sources": sources,
            "scopes": scopes,
            "maxCount": maxCount,
            "groupName": groupName
        }
        qry = ServiceOperationQuery(utility, "SearchPrincipalsUsingContextWeb", params, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def create_wiki_page_in_context_web(context, parameters):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        :type parameters: office365.sharepoint.pages.wiki_page_creation_information.WikiPageCreationInformation
        """
        return_file = File(context)
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "CreateWikiPageInContextWeb", None, parameters, "parameters", return_file)
        qry.static = True
        context.add_query(qry)
        return return_file

    @staticmethod
    def send_email(context, properties):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        :type properties: office365.sharepoint.utilities.email_properties.EmailProperties
        """
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "SendEmail", None, properties, "properties")
        qry.static = True
        context.add_query(qry)

    @property
    def entity_type_name(self):
        return "SP.Utilities.Utility"
