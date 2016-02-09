from client.auth.AuthenticationContext import AuthenticationContext
from client.ClientRequest import ClientRequest

listTitle = "Tasks"

def readListItems(url,ctxAuth):
    "Read list items example"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items".format(listTitle)   #Web resource endpoint

    print "Retriving list items from List {0}".format(listTitle)
    data = request.executeQuery(requestUrl=requestUrl)
    for item in data['d']['results']:
        print "Item title: {0}".format(item["Title"])


def createListItem(url,ctxAuth):
    "Create list item example"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items".format(listTitle)   #Web resource endpoint

    print "Creating list item..."
    itemPayload = {'__metadata': { 'type': 'SP.Data.TasksListItem' }, 'Title': 'New Task'}
    data = request.executeQuery(requestUrl=requestUrl,data=itemPayload)

    if 'error' in data:
        print "An error occured while creating list item: {0}".format(data['error']['message']['value'])
        return None
    print "Task has been succesfully [created]"
    return data['d']

def updateListItem(url,ctxAuth,item):
    "Update list item example"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items({1})".format(listTitle,item['Id'])   #Web resource endpoint

    print "Updating list item..."
    itemPayload = {'__metadata': { 'type': 'SP.Data.TasksListItem' }, 'Title': 'New Task (updated)'}
    headers = {
        'IF-MATCH': '*',
        'X-HTTP-Method': 'MERGE'
    }
    data = request.executeQuery(requestUrl=requestUrl,headers = headers, data=itemPayload)

    if 'error' in data:
        print "An error occured while updating list item: {0}".format(data['error']['message']['value'])
        return None
    print "Task has been succesfully [updated]"


def deleteListItem(url,ctxAuth,item):
    "Delete list item example"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items({1})".format(listTitle,item['Id'])   #Web resource endpoint

    print "Deleting list item..."
    headers = {
        'IF-MATCH': '*',
        'X-HTTP-Method': 'DELETE'
    }
    data = request.executeQuery(requestUrl=requestUrl,headers = headers)

    if 'error' in data:
        print "An error occured while deleting list item: {0}".format(data['error']['message']['value'])
        return None
    print "Task has been succesfully [deleted]"
    
        