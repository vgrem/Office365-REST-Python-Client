from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Union

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.files.file import File
from office365.sharepoint.pages.wiki_page_creation_information import (
    WikiPageCreationInformation,
)
from office365.sharepoint.principal.source import PrincipalSource
from office365.sharepoint.principal.type import PrincipalType
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.utilities.email_properties import EmailProperties
from office365.sharepoint.utilities.principal_info import PrincipalInfo

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class Utility(Entity):
    """
    Provides tools for converting date and time formats, for obtaining information from user names,
    for modifying access to sites, and for various other tasks in managing deployment.
    """

    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("SP.Utilities.Utility")
        return self._resource_path

    @staticmethod
    def create_email_body_for_invitation(context: ClientContext, page_address: str) -> ClientResult[str]:
        """Creates the contents of the e-mail message used to invite users to a document or resource in a site

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            page_address (str): Specifies part of the display name for the document or resource.
        """
        return_type = ClientResult(context, str())
        utility = Utility(context)
        payload = {"pageAddress": str(SPResPath.create_absolute(context.base_url, page_address))}
        qry = ServiceOperationQuery(
            utility,
            "CreateEmailBodyForInvitation",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_current_user_email_addresses(context: ClientContext) -> ClientResult[str]:
        """Returns the email addresses of the current user. If more than one email address exists for the current user,
        returns a list of email addresses separated by semicolons.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
        """
        result = ClientResult(context, str())
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "GetCurrentUserEmailAddresses", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_user_permission_levels(
        context: ClientContext,
    ) -> ClientResult[StringCollection]:
        """
        Retrieves a collection of permission levels of the current user on the web.
        """
        return_type = ClientResult(context, StringCollection())
        utility = Utility(context)
        qry = ServiceOperationQuery(utility, "GetUserPermissionLevels", None, None, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def search_principals_using_context_web(
        context: ClientContext,
        s_input: str,
        sources: str,
        scopes: int,
        max_count: int,
        group_name: Optional[str] = None,
    ) -> ClientResult[StringCollection]:
        """Returns the collection of principals that partially or uniquely matches the specified search criteria in the
        context of the current Web site

        Args:
            s_input (str): Specifies the value to be used when searching for a principal.
            sources (str): Specifies the source to be used when searching for a principal.
            scopes (int): Specifies the type to be used when searching for a principal.
            max_count (int): Specifies the maximum number of principals to be returned.
            group_name (str or None): Specifies the name of a site collection group in the site collection that
                contains the current Web site. The collection of users in this site collection group is used when
                searching for a principal.
            context (office365.sharepoint.client_context.ClientContext):
        """
        return_type = ClientResult(context, StringCollection())
        utility = Utility(context)
        params = {
            "input": s_input,
            "sources": sources,
            "scopes": scopes,
            "maxCount": max_count,
            "groupName": group_name,
        }
        qry = ServiceOperationQuery(utility, "SearchPrincipalsUsingContextWeb", params, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_wiki_page_in_context_web(
        context: ClientContext,
        parameters: WikiPageCreationInformation,
        return_type: Optional[File] = None,
    ) -> File:
        """
        Creates a wiki page.
        """
        if return_type is None:
            return_type = File(context)
        utility = Utility(context)
        payload = {"parameters": parameters}
        qry = ServiceOperationQuery(
            utility,
            "CreateWikiPageInContextWeb",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def send_email(context: ClientContext, properties: EmailProperties) -> Utility:
        """This method is a static method.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            properties (office365.sharepoint.utilities.email_properties.EmailProperties):
        """
        utility = Utility(context)
        payload = {"properties": properties}
        qry = ServiceOperationQuery(utility, "SendEmail", None, payload, None, None, True)
        context.add_query(qry)
        return utility

    @staticmethod
    def unmark_discussion_as_featured(context: ClientContext, list_id: str, topic_ids: str) -> Utility:
        """This method is a static method.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            list_id (str):
            topic_ids (str):
        """
        utility = Utility(context)
        payload = {"listID": list_id, "topicIDs": topic_ids}
        qry = ServiceOperationQuery(utility, "UnmarkDiscussionAsFeatured", None, payload, None, None, True)
        context.add_query(qry)
        return utility

    @staticmethod
    def expand_groups_to_principals(
        context: ClientContext,
        inputs: List[str],
        max_count: Optional[int] = None,
        return_type: Optional[ClientResult[ClientValueCollection[PrincipalInfo]]] = None,
    ):
        """Expands groups to a collection of principals.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            inputs (list[str]): A collection of groups to be expanded.
            max_count (int): Specifies the maximum number of principals to be returned.
            return_type (ClientResult):
        """
        binding_type = Utility(context)
        payload = {"inputs": inputs, "maxCount": max_count}
        if return_type is None:
            return_type = ClientResult(context, ClientValueCollection(PrincipalInfo))
        qry = ServiceOperationQuery(binding_type, "ExpandGroupsToPrincipals", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def log_custom_app_error(context: ClientContext, error: str) -> ClientResult[int]:
        """Logs an error from a SharePoint Add-in. The return value indicates the success or failure of this operation.
        These errors are of interest to administrators who monitor such apps (2).

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            error (str): Error string to log
        """
        utility = Utility(context)
        payload = {
            "error": error,
        }
        return_type = ClientResult(context, int())
        qry = ServiceOperationQuery(utility, "LogCustomAppError", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def resolve_principal_in_current_context(
        context: ClientContext,
        string_input: str,
        scopes: Union[PrincipalType, int] = PrincipalType.All,
        sources: Union[PrincipalSource, int] = PrincipalSource.All,
        input_is_email_only: Optional[bool] = None,
        add_to_user_info_list: Optional[bool] = None,
        match_user_info_list: Optional[bool] = None,
    ) -> ClientResult[PrincipalInfo]:
        """Returns information about a principal that matches the specified search criteria in the context of the current
        Web site.

        Both ``scopes`` and ``sources`` are OData ``Edm.Int32`` flags and are required
        by the service: sent as ``null`` they make the operation answer ``null`` for
        every input rather than report a bad request.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            string_input (str): Specifies the value to be used when searching for a principal.
            scopes (PrincipalType): Specifies the type to be used when searching for a principal.
            sources (PrincipalSource): Specifies the source to be used when searching for a principal.
            input_is_email_only (bool): Specifies whether only the e-mail address is used when searching for a principal
            add_to_user_info_list (bool): Specifies whether to add the principal to the user information list.
            match_user_info_list (bool): Specifies whether to return the principal found in the user information list.
        """
        utility = Utility(context)
        payload = {
            "input": string_input,
            "scopes": scopes.value if isinstance(scopes, Enum) else scopes,
            "sources": sources.value if isinstance(sources, Enum) else sources,
            "inputIsEmailOnly": input_is_email_only,
            "addToUserInfoList": add_to_user_info_list,
            "matchUserInfoList": match_user_info_list,
        }
        return_type = ClientResult(context, PrincipalInfo())
        qry = ServiceOperationQuery(
            utility,
            "ResolvePrincipalInCurrentContext",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Utilities.Utility"
