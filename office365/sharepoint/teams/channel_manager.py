from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.sites.team_site_data import TeamSiteData
from office365.sharepoint.teams.channel import TeamChannel

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.teams.manage_channel_capabilities_request import (
        ManageChannelCapabilitiesRequest,
    )


class TeamChannelManager(Entity):
    """This class is a placeholder for all TeamChannel related methods."""

    @staticmethod
    def add_team_channel(context, channel_url, private_channel=False, private_channel_group_owner=None):
        """Create Team Channel based folder with specific prodID.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client context
            channel_url (str): Team channel URL to be stored in the folder metadata.
            private_channel (bool):
            private_channel_group_owner (str):
        """
        manager = TeamChannelManager(context)
        payload = {
            "teamChannelUrl": channel_url,
            "privateChannel": private_channel,
            "privateChannelGroupOwner": private_channel_group_owner,
        }
        return_type = TeamChannel(context)
        qry = ServiceOperationQuery(manager, "AddTeamChannel", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_team_site_data(context, ignore_validation: bool = True):
        """Args:
        context (office365.sharepoint.client_context.ClientContext): SharePoint client context
        ignore_validation (bool):
        """
        payload = {
            "ignoreValidation": ignore_validation,
        }
        return_type = TeamSiteData(context)
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "GetTeamSiteData",
            None,
            payload,
            None,
            return_type,
        )
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def save_conversations(
        context, list_url: str, list_item_id: int, updated_conversations_object: str
    ) -> "TeamChannelManager":
        """Args:
        context (office365.sharepoint.client_context.ClientContext): SharePoint client context
        list_url (str):
        list_item_id (int):
        updated_conversations_object (str):
        """
        payload = {
            "listUrl": list_url,
            "listItemId": list_item_id,
            "updatedConversationsObject": updated_conversations_object,
        }
        binding_type = TeamChannelManager(context)
        qry = ServiceOperationQuery(binding_type, "SaveConversations", None, payload, is_static=True)
        context.add_query(qry)
        return binding_type

    @staticmethod
    def sync_teamsite_settings(context):
        """Args:
        context (office365.sharepoint.client_context.ClientContext): SharePoint client context
        """
        return_type = TeamSiteData(context)
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "SyncTeamSiteSettings",
            return_type=return_type,
            is_static=True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def archive_team_channel_by_id(context: ClientContext, folder_id: UUID) -> ClientResult[bool]:
        """ArchiveTeamChannelById operation.

        Args:
            folder_id (UUID):
                folderId parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context), "ArchiveTeamChannelById", None, {"folderId": folder_id}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def archive_team_channel_by_path(context: ClientContext, folder_path: ResourcePath) -> ClientResult[bool]:
        """ArchiveTeamChannelByPath operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "ArchiveTeamChannelByPath",
            None,
            {"folderPath": folder_path},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def demote_team_channel_by_id(context: ClientContext, folder_id: UUID) -> ClientResult[bool]:
        """DemoteTeamChannelById operation.

        Args:
            folder_id (UUID):
                folderId parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context), "DemoteTeamChannelById", None, {"folderId": folder_id}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def demote_team_channel_by_path(context: ClientContext, decoded_url: str) -> ClientResult[bool]:
        """DemoteTeamChannelByPath operation.

        Args:
            decoded_url (str):
                DecodedUrl parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "DemoteTeamChannelByPath",
            None,
            {"DecodedUrl": decoded_url},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_conversations(context: ClientContext, list_url: str, list_item_id: int) -> ClientResult[str]:
        """GetConversations operation.

        Args:
            list_url (str):
                listUrl parameter
            list_item_id (int):
                listItemId parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "GetConversations",
            None,
            {"listUrl": list_url, "listItemId": list_item_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def manage_channel_capabilities(context: ClientContext, request: ManageChannelCapabilitiesRequest) -> None:
        """ManageChannelCapabilities operation.

        Args:
            request (ManageChannelCapabilitiesRequest):
                request parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        qry = ServiceOperationQuery(
            TeamChannelManager(context), "ManageChannelCapabilities", None, {"request": request}, None, None, True
        )
        context.add_query(qry)

    @staticmethod
    def promote_to_team_channel_by_id(
        context: ClientContext, folder_id: UUID, team_channel_url: str, channel_name: str
    ) -> ClientResult[bool]:
        """PromoteToTeamChannelById operation.

        Args:
            folder_id (UUID):
                folderId parameter
            team_channel_url (str):
                teamChannelUrl parameter
            channel_name (str):
                channelName parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "PromoteToTeamChannelById",
            None,
            {"folderId": folder_id, "teamChannelUrl": team_channel_url, "channelName": channel_name},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def promote_to_team_channel_by_path(
        context: ClientContext, decoded_url: str, team_channel_url: str, channel_name: str
    ) -> ClientResult[bool]:
        """PromoteToTeamChannelByPath operation.

        Args:
            decoded_url (str):
                DecodedUrl parameter
            team_channel_url (str):
                teamChannelUrl parameter
            channel_name (str):
                channelName parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "PromoteToTeamChannelByPath",
            None,
            {"DecodedUrl": decoded_url, "teamChannelUrl": team_channel_url, "channelName": channel_name},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def stamp_lwg_id_on_private_channel_site(context: ClientContext, id_lwg: UUID) -> ClientResult[bool]:
        """StampLWGIdOnPrivateChannelSite operation.

        Args:
            id_lwg (UUID):
                idLWG parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "StampLWGIdOnPrivateChannelSite",
            None,
            {"idLWG": id_lwg},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def unarchive_team_channel_by_id(context: ClientContext, folder_id: UUID) -> ClientResult[bool]:
        """UnarchiveTeamChannelById operation.

        Args:
            folder_id (UUID):
                folderId parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "UnarchiveTeamChannelById",
            None,
            {"folderId": folder_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def unarchive_team_channel_by_path(context: ClientContext, folder_path: ResourcePath) -> ClientResult[bool]:
        """UnarchiveTeamChannelByPath operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
        """
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context),
            "UnarchiveTeamChannelByPath",
            None,
            {"folderPath": folder_path},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def unstamp_lwg_id_on_private_channel_site(context: ClientContext) -> ClientResult[bool]:
        """UnstampLWGIdOnPrivateChannelSite operation."""
        from office365.sharepoint.teams.channel_manager import TeamChannelManager

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            TeamChannelManager(context), "UnstampLWGIdOnPrivateChannelSite", None, {}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
