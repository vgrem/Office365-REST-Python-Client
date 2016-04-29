from random import randint

from client.client_context import ClientContext
from client.auth.authentication_context import AuthenticationContext
from settings import settings


def load_web(ctx):
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print "Web site url: {0}".format(web.properties['ServerRelativeUrl'])
    return web


def update_web(web):
    propertiesToUpdate = {'Title': "New web site"}
    web.update(propertiesToUpdate)
    web.context.execute_query()
    print "Web site has been updated"


def create_web(ctx):
    web_prefix = str(randint(0, 100))
    creation_info = {'Url': "workspace" + web_prefix, 'Title': "Workspace"}
    newWeb = ctx.web.webs.add(creation_info)
    ctx.execute_query()
    print "Web site {0} has been created".format(newWeb.properties['ServerRelativeUrl'])
    return newWeb


def delete_web(web):
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
        update_web(web)
        delete_web(web)

    else:
        print ctxAuth.get_last_error()
