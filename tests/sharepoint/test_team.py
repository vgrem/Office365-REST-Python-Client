from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.teams.channel_manager import TeamChannelManager
from tests import test_team_site_url, test_user_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestTeam(SPTestCase):

    def test1_get_team_site_data(self):
        return_type = TeamChannelManager.get_team_site_data(self.client).execute_query()
        self.assertIsNotNone(return_type.properties.get("SiteUrl"))

    def test2_get_current_user_joined_teams(self):
        my_client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
        result = my_client.group_site_manager.get_current_user_joined_teams().execute_query()
        self.assertIsNotNone(result.value)
