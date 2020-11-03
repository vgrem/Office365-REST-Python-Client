import adal
from settings import settings

from office365.graph_client import GraphClient


def get_token_for_user():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


client = GraphClient(get_token_for_user)

deleted_groups = client.directory.deletedGroups.get().execute_query()
# deleted_users = client.directory.deletedUsers.get().execute_query()
groups_count = len(deleted_groups)

for index, deleted_grp in enumerate(deleted_groups):
    print("({0} of {1}) Deleting {2} group ...".format(index + 1, groups_count, deleted_grp.properties['displayName']))
    deleted_grp.delete_object()
    client.execute_query()
    print("Group deleted.")
