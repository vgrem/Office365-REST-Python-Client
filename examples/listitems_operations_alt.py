from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.runtime.client_request import ClientRequest
from settings import settings


def read_list_items(web_url, ctx_auth, list_title):
    """Read list items example"""
    request = ClientRequest(web_url, ctx_auth)
    request_url = "{0}/_api/web/lists/getbyTitle('{1}')/items".format(web_url, list_title)  # Web resource endpoint

    print "Retrieving list items from List {0}".format(list_title)
    data = request.execute_query_direct(request_url=request_url)
    for item in data['d']['results']:
        print "Item title: {0}".format(item["Title"])


def create_list_item(web_url, ctx_auth, list_title):
    """Create list item example"""
    request = ClientRequest(web_url, ctx_auth)
    request_url = "{0}/_api/web/lists/getbyTitle('{1}')/items".format(web_url, list_title)  # Web resource endpoint

    print "Creating list item..."
    item_payload = {'__metadata': {'type': 'SP.Data.TasksListItem'}, 'Title': 'New Task'}
    data = request.execute_query_direct(request_url=request_url, data=item_payload)
    print "Task {0} has been successfully [created]".format(data['d']['Title'])
    return data['d']


def update_list_item(web_url, ctx_auth, list_title, item_id):
    """Update list item example"""
    request = ClientRequest(web_url, ctx_auth)
    request_url = "{0}/_api/web/lists/getbyTitle('{1}')/items({2})".format(web_url, list_title, item_id)
    print "Updating list item..."
    item_payload = {'__metadata': {'type': 'SP.Data.TasksListItem'}, 'Title': 'New Task (updated)'}
    headers = {
        'IF-MATCH': '*',
        'X-HTTP-Method': 'MERGE'
    }
    request.execute_query_direct(request_url=request_url, headers=headers, data=item_payload)
    print "Task has been successfully [updated]"


def delete_list_item(web_url, ctx_auth, list_title, item_id):
    """Delete list item example"""
    request = ClientRequest(web_url, ctx_auth)
    request_url = "{0}/_api/web/lists/getbyTitle('{1}')/items({2})".format(web_url, list_title, item_id)
    print "Deleting list item..."
    headers = {
        'IF-MATCH': '*',
        'X-HTTP-Method': 'DELETE'
    }
    request.execute_query_direct(request_url=request_url, headers=headers)
    print "Task has been successfully [deleted]"


if __name__ == '__main__':
    context_auth = AuthenticationContext(url=settings['url'])
    if context_auth.acquire_token_for_user(username=settings['username'], password=settings['password']):

        read_list_items(settings['url'], context_auth, "Tasks")
        task_item = create_list_item(settings['url'], context_auth, "Tasks")
        update_list_item(settings['url'], context_auth, "Tasks", task_item['Id'])
        delete_list_item(settings['url'], context_auth, "Tasks", task_item['Id'])

    else:
        print context_auth.get_last_error()
