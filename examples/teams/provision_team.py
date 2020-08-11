import uuid

from settings import settings

from office365.graph.directory.groupProfile import GroupProfile
from office365.graph.graph_client import GraphClient


def acquire_token(auth_ctx):
    """
    Get token
    :type auth_ctx: adal.AuthenticationContext
    """
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


def create_group_for_team(groups, name):
    grp_properties = GroupProfile(name)
    grp_properties.securityEnabled = False
    grp_properties.mailEnabled = True
    grp_properties.groupTypes = ["Unified"]
    target_group = groups.add(grp_properties)
    return target_group


def print_failure(retry_number):
    print(f"{retry_number}: trying to create a team...")


client = GraphClient(settings['tenant'], acquire_token)

group_name = "Team_" + uuid.uuid4().hex
result = client.teams.create(group_name)
client.execute_query_retry(max_retry=5, on_failure=print_failure)
print("Team has been provisioned")

channels = result.value.channels
client.load(channels)
client.execute_query()
