from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

listTitle = "Tasks"


def read_list_items():
    print("Read list items example...")
    list_object = ctx.web.lists.get_by_title(listTitle)
    items = list_object.get_items()
    ctx.load(items)
    ctx.execute_query()

    for item in items:
        print("Item title: {0}".format(item.properties["Title"]))


def filter_list_items():
    print("OData query against list items example...")
    list_object = ctx.web.lists.get_by_title(listTitle)
    # items = list_object.get_items().top(1).select("Id,Title")
    items = list_object.get_items().select("Id,Title").filter("AssignedTo ne null")
    ctx.load(items)
    ctx.execute_query()

    for item in items:
        print("Item title: {0}".format(item.properties["Title"]))


def create_list_item():
    print("Create list item example...")
    list_object = ctx.web.lists.get_by_title(listTitle)
    item_properties = {'__metadata': {'type': 'SP.Data.TasksListItem'}, 'Title': 'New Task'}
    item = list_object.add_item(item_properties)
    ctx.execute_query()
    print("List item '{0}' has been created.".format(item.properties["Title"]))


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['user_credentials']['username'], password=settings['user_credentials']['password']):
        ctx = ClientContext(settings['url'], ctxAuth)

        # read_list_items()
        # create_list_item()
        filter_list_items()

    else:
        print(ctxAuth.get_last_error())
