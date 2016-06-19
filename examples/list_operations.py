from random import randint

from client.client_context import ClientContext
from client.runtime.auth.authentication_context import AuthenticationContext
from settings import settings

listTitle = "Tasks"


def readListItemById(ctx):
    print "Read list item by id example..."
    list = ctx.web.lists.get_by_title(listTitle)
    items = list.get_items()
    ctx.load(items)
    ctx.execute_query()

    for item in items:
        itemId = item.properties["Id"]
        curItem = list.get_item_by_id(itemId)
        ctx.load(curItem)
        ctx.execute_query()
        print "List item title: {0}".format(curItem.properties["Title"])


def read_list(list):
    print "Read list items example..."
    ctx = list.context
    ctx.load(list)
    ctx.execute_query()
    print "List title: {0}".format(list.properties["Title"])

    listSiteAssets = ctx.web.lists.ensure_site_assets_library()
    ctx.load(listSiteAssets)
    ctx.execute_query()
    print "Site Assets title: {0}".format(listSiteAssets.properties["Title"])

    listSitePages = ctx.web.lists.ensure_site_pages_library()
    ctx.load(listSitePages)
    ctx.execute_query()
    print "Site Pages title: {0}".format(listSitePages.properties["Title"])


def create_random_tasks_list(ctx):
    print "Create list example..."
    listTitle = "Tasks" + str(randint(0, 100))
    listProperties = {'__metadata': {'type': 'SP.List'}, 'AllowContentTypes': True, 'BaseTemplate': 171,
                      'Title': listTitle}
    list = ctx.web.lists.add(listProperties)
    ctx.execute_query()

    print "List {0} has been created".format(list.properties["Title"])
    return list


def update_list(list):
    print "Update list example..."
    ctx = list.context
    listProperties = {'__metadata': {'type': 'SP.List'}, 'Description': list.properties["Title"]}
    list.update(listProperties)
    ctx.execute_query()

    print "List {0} has been updated".format(list.properties["Title"])


def delete_list(list):
    print "Delete list example..."
    listTitle = list.properties["Title"]
    ctx = list.context
    list.delete_object()
    ctx.execute_query()
    print "List {0} has been deleted".format(listTitle)


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctxAuth)
        #listTitle = "Tasks"
        #list = ctx.Web.Lists.getByTitle(listTitle)
        #readList(list)
        list_obj = create_random_tasks_list(ctx)
        update_list(list_obj)
        delete_list(list_obj)
        # readListItemById(ctx)
    else:
        print ctxAuth.get_last_error()
