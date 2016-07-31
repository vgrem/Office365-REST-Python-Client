from random import randint
from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.sharepoint.client_context import ClientContext
from settings import settings


def load_web(context):
    cur_web = context.web
    context.load(cur_web)
    context.execute_query()
    print "Web site url: {0}".format(cur_web.properties['ServerRelativeUrl'])
    return cur_web


def update_web():
    properties_to_update = {'Title': "New web site"}
    web.update(properties_to_update)
    web.context.execute_query()
    print "Web site has been updated"


def create_web(context):
    web_prefix = str(randint(0, 100))
    creation_info = {'Url': "workspace" + web_prefix, 'Title': "Workspace"}
    new_web = context.web.webs.add(creation_info)
    context.execute_query()
    print "Web site {0} has been created".format(new_web.properties['ServerRelativeUrl'])
    return new_web


def delete_web():
    web.delete_object()
    web.context.execute_query()
    print "Web site has been deleted"


def list_site_users(ctx):
    users = ctx.web.site_users
    ctx.load(users)
    ctx.execute_query()
    print "The list of users:"
    for user in users:
        print "User title: {0}".format(user.properties["Title"])


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctxAuth)

        # web = load_web(ctx)
        web = create_web(ctx)
        update_web()
        delete_web()

    else:
        print ctxAuth.get_last_error()
