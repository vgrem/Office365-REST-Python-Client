from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.sharepoint.client_context import ClientContext
from settings import settings

listTitle = "Documents"


def print_list_views(ctx):
    """Read list view by title example"""
    list_object = ctx.web.lists.get_by_title(listTitle)
    views = list_object.views
    ctx.load(views)
    ctx.execute_query()
    for view in views:
        # print "View title: {0}".format(view.Properties["Title"])

        viewTitle = view.properties["Title"]
        curView = views.get_by_title(viewTitle)
        ctx.load(curView)
        ctx.execute_query()
        print "View title: {0}".format(curView.properties["Title"])


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctxAuth)

        print_list_views(ctx)

    else:
        print ctxAuth.get_last_error()
