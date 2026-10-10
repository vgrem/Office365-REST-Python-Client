from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.portal.channels.info_collection import ChannelInfoCollection
from office365.sharepoint.portal.ensureteamforgroupexresponse import (
    EnsureTeamForGroupExResponse,
)
from office365.sharepoint.portal.groups.creation_context import GroupCreationContext
from office365.sharepoint.portal.groups.creation_information import (
    GroupCreationInformation,
)
from office365.sharepoint.portal.groups.creation_params import GroupCreationParams
from office365.sharepoint.portal.groups.site_info import GroupSiteInfo
from office365.sharepoint.portal.groups.siteconversioninfo import (
    GroupSiteConversionInfo,
)
from office365.sharepoint.portal.orglabels.context_list import OrgLabelsContextList
from office365.sharepoint.portal.parentgroup import ParentGroup
from office365.sharepoint.portal.pintoteamparams import PinToTeamParams
from office365.sharepoint.portal.pintoteamresponse import PinToTeamResponse
from office365.sharepoint.portal.teams.recent_and_joined_response import (
    RecentAndJoinedTeamsResponse,
)

if TYPE_CHECKING:
    from office365.sharepoint.sites.site import Site


class GroupSiteManager(ClientObject):
    """Management of Group Sites in SharePoint. Group Sites, also known as Microsoft 365 Groups,
    provide collaboration spaces that integrate with various Microsoft 365 services like Teams, Outlook, and Planner.
    """

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("GroupSiteManager")
        super().__init__(context, resource_path)

    def can_user_create_group(self) -> ClientResult[bool]:
        """Determines if the current user can create group site"""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CanUserCreateGroup", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_group_for_site(
        self,
        display_name: str,
        alias: str,
        is_public: Optional[bool] = None,
        optional_params: Optional[GroupCreationParams] = None,
    ):
        """Create a modern site

        Args:
            display_name (str):
            alias (str):
            is_public (bool or None):
            optional_params (office365.sharepoint.portal.group_creation_params.GroupCreationParams or None):
        """
        payload = {"displayName": display_name, "alias": alias, "isPublic": is_public, "optionalParams": optional_params}
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "CreateGroupForSite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_group_ex(
        self, display_name: str, alias: str, is_public: bool, optional_params: Optional[GroupCreationParams] = None
    ):
        """
        Creates a modern site
        """
        payload = GroupCreationInformation(display_name, alias, is_public, optional_params or GroupCreationParams())
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "CreateGroupEx", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete(self, site_url: str) -> Self:
        """Deletes a SharePoint Team site

        Args:
            site_url (str):
        """
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "Delete", None, payload)
        self.context.add_query(qry)
        return self

    def ensure_team_for_group(self):
        """ """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "EnsureTeamForGroup", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_group_creation_context(self):
        """ """
        return_type = ClientResult(self.context, GroupCreationContext())
        qry = ServiceOperationQuery(self, "GetGroupCreationContext", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_status(self, group: Union[str, Site]) -> ClientResult[GroupSiteInfo]:
        """Get the status of a SharePoint site"""
        from office365.sharepoint.sites.site import Site

        return_type = ClientResult(self.context, GroupSiteInfo())

        def _get_status(group_id: str | None):
            assert group_id is not None
            qry = ServiceOperationQuery(self, "GetSiteStatus", None, {"groupId": group_id}, None, return_type)

            def _construct_request(request: RequestOptions) -> None:
                request.method = HttpMethod.Get
                request.url += f"?groupId='{group_id}'"

            self.context.add_query(qry).before_execute(_construct_request)

        if isinstance(group, Site):
            group.ensure_property("GroupId").after_execute(lambda _: _get_status(group.group_id))
        else:
            _get_status(group)
        return return_type

    def get_current_user_joined_teams(
        self, get_logo_data: bool = False, force_cache_update: bool = False
    ) -> ClientResult[str]:
        """Get the teams in Microsoft Teams that the current user is a direct member of.

        Args:
            get_logo_data (bool):
            force_cache_update (bool):
        """
        result = ClientResult(self.context, str())
        payload = {"getLogoData": get_logo_data, "forceCacheUpdate": force_cache_update}
        qry = ServiceOperationQuery(self, "GetCurrentUserJoinedTeams", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_current_user_shared_channel_member_groups(self) -> ClientResult[str]:
        """ """
        return_type = ClientResult[str](self.context)
        qry = ServiceOperationQuery(self, "GetCurrentUserSharedChannelMemberGroups", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_team_channels(self, team_id: str, use_staging_endpoint: bool = False) -> ClientResult[bytes]:
        """Retrieves the channels associated with a specific Microsoft 365 Group (or Team)

        Args:
            team_id (str):
            use_staging_endpoint (bool):
        """
        return_type = ClientResult[bytes](self.context)
        payload = {"teamId": team_id, "useStagingEndpoint": use_staging_endpoint}
        qry = ServiceOperationQuery(self, "GetTeamChannels", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_team_channels_direct(self, team_id: str) -> ClientResult[str]:
        """Args:
        team_id (str):
        """
        return_type = ClientResult(self.context, str())
        payload = {"teamId": team_id}
        qry = ServiceOperationQuery(self, "GetTeamChannelsDirect", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_team_channels_with_site_url(self, site_url: str) -> ClientResult[ChannelInfoCollection]:
        """Returns a list of team channels associated with a Microsoft 365 Group.

        Args:
            site_url (str):
        """
        return_type = ClientResult(self.context, ChannelInfoCollection())
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "GetTeamChannelsWithSiteUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def notebook(self, group_id: str) -> ClientResult[str]:
        """Args:
        group_id (str):
        """
        return_type = ClientResult(self.context, str())
        payload = {"groupId": group_id}
        qry = ServiceOperationQuery(self, "Notebook", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recent_and_joined_teams(
        self,
        include_recent: Optional[bool] = None,
        include_teams: Optional[bool] = None,
        include_pinned: Optional[bool] = None,
        existing_joined_teams_data: Optional[str] = None,
    ) -> ClientResult[RecentAndJoinedTeamsResponse]:
        """Retrieves a list of teams that a user has recently accessed or joined

        Args:
            include_recent (bool):
            include_teams (bool):
            include_pinned (bool):
            existing_joined_teams_data (str):
        """
        return_type = ClientResult(self.context, RecentAndJoinedTeamsResponse())
        payload = {
            "includeRecent": include_recent,
            "includeTeams": include_teams,
            "includePinned": include_pinned,
            "existingJoinedTeamsData": existing_joined_teams_data,
        }
        qry = ServiceOperationQuery(self, "RecentAndJoinedTeams", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.GroupSiteManager"

    def cache_current_user_joined_teams_result(self, joined_teams: str) -> ClientResult[str]:
        """CacheCurrentUserJoinedTeamsResult operation.

        Args:
            joined_teams (str): joinedTeams parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "CacheCurrentUserJoinedTeamsResult", None, {"joinedTeams": joined_teams}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def clear_current_user_teams_cache(self) -> Self:
        """ClearCurrentUserTeamsCache operation."""
        qry = ServiceOperationQuery(self, "ClearCurrentUserTeamsCache", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def create(self, group_id: UUID) -> ClientResult[GroupSiteInfo]:
        """Create operation.

        Args:
            group_id (UUID): groupId parameter
        """
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(self, "Create", None, {"groupId": group_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_group(
        self,
        display_name: str,
        alias: str,
        is_public: bool,
        owner_principal_names: list[str],
        description: str,
        creation_options: list[str],
    ) -> ClientResult[GroupSiteInfo]:
        """CreateGroup operation.

        Args:
            display_name (str): displayName parameter
            alias (str): alias parameter
            is_public (bool): isPublic parameter
            owner_principal_names (list[str]): ownerPrincipalNames parameter
            description (str): description parameter
            creation_options (list[str]): creationOptions parameter
        """
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = ServiceOperationQuery(
            self,
            "CreateGroup",
            None,
            {
                "displayName": display_name,
                "alias": alias,
                "isPublic": is_public,
                "ownerPrincipalNames": StringCollection(owner_principal_names),
                "description": description,
                "creationOptions": StringCollection(creation_options),
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_teams_for_group(self, group_id: str, team_template: str) -> ClientResult[str]:
        """CreateTeamsForGroup operation.

        Args:
            group_id (str): groupId parameter
            team_template (str): teamTemplate parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "CreateTeamsForGroup", None, {"groupId": group_id, "teamTemplate": team_template}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def create_teams_nav_link(self, teams_link_url: str, site_url: str) -> Self:
        """CreateTeamsNavLink operation.

        Args:
            teams_link_url (str): teamsLinkUrl parameter
            site_url (str): siteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "CreateTeamsNavLink", None, {"teamsLinkUrl": teams_link_url, "siteUrl": site_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def ensure_team_for_group_ex(self, site_url: str, team_template: str) -> ClientResult[EnsureTeamForGroupExResponse]:
        """EnsureTeamForGroupEx operation.

        Args:
            site_url (str): siteUrl parameter
            team_template (str): teamTemplate parameter
        """
        return_type = ClientResult(self.context, EnsureTeamForGroupExResponse())
        qry = ServiceOperationQuery(
            self, "EnsureTeamForGroupEx", None, {"siteUrl": site_url, "teamTemplate": team_template}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_all_org_labels(self, page_number: int) -> ClientResult[OrgLabelsContextList]:
        """GetAllOrgLabels operation.

        Args:
            page_number (int): pageNumber parameter
        """
        return_type = ClientResult(self.context, OrgLabelsContextList())
        qry = FunctionQuery(self, "GetAllOrgLabels", [page_number], return_type)
        self.context.add_query(qry)
        return return_type

    def get_current_user_team_connected_member_groups(self) -> ClientResult[str]:
        """GetCurrentUserTeamConnectedMemberGroups operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetCurrentUserTeamConnectedMemberGroups", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_group_site_conversion_data(self) -> ClientResult[GroupSiteConversionInfo]:
        """GetGroupSiteConversionData operation."""
        return_type = ClientResult(self.context, GroupSiteConversionInfo())
        qry = FunctionQuery(self, "GetGroupSiteConversionData", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_parent_group_for_channel(self, site_url: str) -> ClientResult[ClientValueCollection[ParentGroup]]:
        """GetParentGroupForChannel operation.

        Args:
            site_url (str): siteUrl parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection[ParentGroup]())
        qry = ServiceOperationQuery(self, "GetParentGroupForChannel", None, {"siteUrl": site_url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_shared_channel_share_point_url(self, tenant_id: str, group_id: UUID) -> ClientResult[str]:
        """GetSharedChannelSharePointUrl operation.

        Args:
            tenant_id (str): tenantId parameter
            group_id (UUID): groupId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetSharedChannelSharePointUrl", None, {"tenantId": tenant_id, "groupId": group_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_site_status(self, group_id: UUID) -> ClientResult[GroupSiteInfo]:
        """GetSiteStatus operation.

        Args:
            group_id (UUID): groupId parameter
        """
        return_type = ClientResult(self.context, GroupSiteInfo())
        qry = FunctionQuery(self, "GetSiteStatus", [group_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_team_channel_files_url(self, team_id: str, channel_id: str) -> ClientResult[bytes]:
        """GetTeamChannelFilesUrl operation.

        Args:
            team_id (str): teamId parameter
            channel_id (str): channelId parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetTeamChannelFilesUrl", None, {"teamId": team_id, "channelId": channel_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_team_channels_ex(self, team_id: str) -> ClientResult[ChannelInfoCollection]:
        """GetTeamChannelsEx operation.

        Args:
            team_id (str): teamId parameter
        """
        return_type = ClientResult(self.context, ChannelInfoCollection())
        qry = ServiceOperationQuery(self, "GetTeamChannelsEx", None, {"teamId": team_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_shared_channel_member_groups(self, user_name: str) -> ClientResult[str]:
        """GetUserSharedChannelMemberGroups operation.

        Args:
            user_name (str): userName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetUserSharedChannelMemberGroups", None, {"userName": user_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_user_team_connected_member_groups(self, user_name: str) -> ClientResult[str]:
        """GetUserTeamConnectedMemberGroups operation.

        Args:
            user_name (str): userName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetUserTeamConnectedMemberGroups", None, {"userName": user_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_valid_site_url_from_alias(self, alias: str, managed_path: str, is_team_site: bool) -> ClientResult[str]:
        """GetValidSiteUrlFromAlias operation.

        Args:
            alias (str): alias parameter
            managed_path (str): managedPath parameter
            is_team_site (bool): isTeamSite parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetValidSiteUrlFromAlias", [alias, managed_path, is_team_site], return_type)
        self.context.add_query(qry)
        return return_type

    def hide_teamify_prompt(self, site_url: str) -> Self:
        """HideTeamifyPrompt operation.

        Args:
            site_url (str): siteUrl parameter
        """
        qry = ServiceOperationQuery(self, "HideTeamifyPrompt", None, {"siteUrl": site_url}, None, None)
        self.context.add_query(qry)
        return self

    def is_teamify_prompt_hidden(self, site_url: str) -> ClientResult[bool]:
        """IsTeamifyPromptHidden operation.

        Args:
            site_url (str): siteUrl parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "IsTeamifyPromptHidden", [site_url], return_type)
        self.context.add_query(qry)
        return return_type

    def pin_to_team(self, request_params: PinToTeamParams) -> ClientResult[PinToTeamResponse]:
        """PinToTeam operation.

        Args:
            request_params (PinToTeamParams): requestParams parameter
        """
        return_type = ClientResult(self.context, PinToTeamResponse())
        qry = ServiceOperationQuery(self, "PinToTeam", None, {"requestParams": request_params}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_shared_channel_sharepoint_url(self, tenant_id: str, group_id: UUID) -> ClientResult[str]:
        """GetSharedChannelSharePointUrl operation.

        Args:
            tenant_id (str):
                tenantId parameter
            group_id (UUID):
                groupId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetSharedChannelSharePointUrl", None, {"tenantId": tenant_id, "groupId": group_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
