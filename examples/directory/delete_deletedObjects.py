from settings import settings

from office365.graph.graph_client import GraphClient


def get_token_for_user(auth_ctx):
    """

    :type auth_ctx: adal.AuthenticationContext
    """
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


client = GraphClient(settings['tenant'], get_token_for_user)

deleted_groups = client.directory.deletedGroups
client.load(deleted_groups)
deleted_users = client.directory.deletedUsers
client.load(deleted_users)
client.execute_query()
groups_count = len(deleted_groups)

for index, deleted_grp in enumerate(deleted_groups):
    print("({0} of {1}) Deleting {2} group ...".format(index + 1, groups_count, deleted_grp.properties['displayName']))
    deleted_grp.delete_object()
    client.execute_query()
    print("Group deleted.")
