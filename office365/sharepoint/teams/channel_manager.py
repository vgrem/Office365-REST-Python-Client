from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.team_site_data import TeamSiteData
from office365.sharepoint.teams.channel import TeamChannel


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

    @staticmethod
    def get_team_site_data(context, ignore_validation=True):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param bool ignore_validation:
        """
        manager = TeamChannelManager(context)
        payload = {
            "ignoreValidation": ignore_validation,
        }
        return_type = TeamSiteData(context)
        qry = ServiceOperationQuery(manager, "GetTeamSiteData", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type
