from random import randint
from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.web_creation_information import WebCreationInformation


def load_web(context):
    cur_web = context.web
    context.load(cur_web)
    context.execute_query()
    print("Web site url: {0}".format(cur_web.properties['ServerRelativeUrl']))
    return cur_web


def update_web(web_to_update):
    web_to_update.set_property('Title', "New web site")
    web_to_update.update()
    web_to_update.context.execute_query()
    print("Web site has been updated")


def create_web(context):
    web_prefix = str(randint(0, 100))
    creation_info = WebCreationInformation()
    creation_info.Url = "workspace" + web_prefix
    creation_info.Title = "Workspace"
    new_web = context.web.webs.add(creation_info)
    context.execute_query()
    print("Web site {0} has been created".format(new_web.properties['ServerRelativeUrl']))
    return new_web


def delete_web(web_to_delete):
    web_to_delete.delete_object()
    web_to_delete.context.execute_query()
    print("Web site has been deleted")


def list_site_users(ctx):
    users = ctx.web.site_users
    ctx.load(users)
    ctx.execute_query()
    print("The list of users:")
    for user in users:
        print("User title: {0}".format(user.properties["Title"]))


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                      password=settings['user_credentials']['password']):
        ctx = ClientContext(settings['url'], ctxAuth)
        # web = load_web(ctx)
        web = create_web(ctx)
        update_web(web)
        delete_web(web)
    else:
        print(ctxAuth.get_last_error())
