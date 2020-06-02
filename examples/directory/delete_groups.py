from office365.graph.graph_client import GraphClient
from settings import settings


def get_token_for_user(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


client = GraphClient(settings['tenant'], get_token_for_user)

groups = client.groups
client.load(groups)
client.execute_query()
no = 1
groups_count = len(groups)
for grp in groups:
    print("({0} of {1}) Deleting {2} group ...".format(no, groups_count, grp.properties['displayName']))
    # 1st step: delete group
    grp.delete_object()
    client.execute_query()

    # 2nd step: permanently delete (deleted) group
    deleted_group = client.directory.deletedGroups[grp.id]
    deleted_group.delete_object()
    client.execute_query()
    print("Group deleted.")
    no += 1
