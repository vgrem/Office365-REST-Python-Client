from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.teams.team_channel import TeamChannel


class TeamChannelManager(BaseEntity):
    """This class is a placeholder for all TeamChannel related methods."""

    @staticmethod
    def add_team_channel(context, channel_url, private_channel=False, private_channel_group_owner=None):
        """
        Create Team Channel based folder with specific prodID.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param str channel_url:  Team channel URL to be stored in the folder metadata.
        :param bool private_channel:
        :param str private_channel_group_owner:
        """
        manager = TeamChannelManager(context)
        payload = {
            "teamChannelUrl": channel_url,
            "privateChannel": private_channel,
            "privateChannelGroupOwner": private_channel_group_owner
        }
        return_type = TeamChannel(context)
        qry = ServiceOperationQuery(manager, "AddTeamChannel", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type
