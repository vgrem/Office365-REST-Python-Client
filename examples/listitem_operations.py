from client.client_context import ClientContext
from client.auth.authentication_context import AuthenticationContext
from settings import settings

listTitle = "Tasks"


def read_list_items(ctx):
    """Read list items example"""
    list = ctx.web.lists.get_by_title(listTitle)
    items = list.get_items()
    ctx.load(items)
    ctx.execute_query()

    for item in items:
        print "Item title: {0}".format(item.properties["Title"])


def create_list_item(ctx):
    "Create list item example"
    list = ctx.web.lists.get_by_title(listTitle)
    itemProperties = {'__metadata': {'type': 'SP.Data.TasksListItem'}, 'Title': 'New Task'}
    item = list.add_item(itemProperties)
    ctx.execute_query()
    print "List item '{0}' has been created.".format(item.properties["Title"])


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctxAuth)

        read_list_items(ctx)
        create_list_item(ctx)

    else:
        print ctxAuth.get_last_error()
