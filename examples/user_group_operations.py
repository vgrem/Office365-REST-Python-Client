from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.sharepoint.client_context import ClientContext
from settings import settings


def read_groups(ctx):
    """Read site groups example"""
    groups = ctx.web.site_groups
    ctx.load(groups)
    ctx.execute_query()

    for group in groups:
        print "Group title: {0}".format(group.properties["Title"])


def crud_group(ctx):
    """Create a group"""
    groupName = "Orders Approvers221"
    groups = ctx.web.site_groups
    groupProperties = {'__metadata': {'type': 'SP.Group'}, 'Title': groupName}
    group = groups.add(groupProperties)
    ctx.execute_query()
    print "Group : {0} has been created".format(group.properties["Title"])

    "Retrieve group users"
    users = group.users
    ctx.load(users)
    ctx.execute_query()
    for user in users:
        print "User : {0}".format(user.properties["Title"])

    "Remove a group"
    groups.remove_by_login_name(groupName)
    ctx.execute_query()
    print "Group : {0} has been deleted".format(groupName)


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctxAuth)

        read_groups(ctx)
        #crudGroup(ctx)

    else:
        print ctxAuth.get_last_error()
