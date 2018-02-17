from examples.settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.caml_query import CamlQuery
from office365.sharepoint.client_context import ClientContext

list_title = "Documents"
view_title = "All Documents"


def print_list_views(ctx):
    """Read list view by title example"""
    list_object = ctx.web.lists.get_by_title(list_title)
    views = list_object.views
    ctx.load(views)
    ctx.execute_query()
    for view in views:
        # print "View title: {0}".format(view.Properties["Title"])

        cur_view_title = view.properties["Title"]
        cur_view = views.get_by_title(cur_view_title)
        ctx.load(cur_view)
        ctx.execute_query()
        print("View title: {0}".format(cur_view.properties["Title"]))


def print_view_items(ctx):
    """Example demonstrates how to retrieve View items"""

    list_object = ctx.web.lists.get_by_title(list_title)
    # 1.get View query
    view = list_object.views.get_by_title(view_title)
    ctx.load(view, "ViewQuery")
    ctx.execute_query()

    # 2.get items for View query
    qry = CamlQuery()
    qry.ViewXml = "<View><Where>{0}</Where></View>".format(view.properties["ViewQuery"])
    items = list_object.get_items(qry)
    ctx.load(items)
    ctx.execute_query()

    for item in items:
        print("Item title: {0}".format(item.properties["Title"]))


if __name__ == '__main__':
    ctx_auth = AuthenticationContext(url=settings['url'])
    if ctx_auth.acquire_token_for_app(client_id=settings['client_credentials']['client_id'],
                                      client_secret=settings['client_credentials']['client_secret']):
        ctx = ClientContext(settings['url'], ctx_auth)

        # print_list_views(ctx)
        print_view_items(ctx)

    else:
        print(ctx_auth.get_last_error())
