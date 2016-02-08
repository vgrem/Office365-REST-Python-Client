from client.ClientRequest import ClientRequest

listTitle = "Tasks"

def readListItems(url,ctxAuth):
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items".format(listTitle)   #Web resource endpoint

    print "Retriving list items from List {0}".format(listTitle)
    data = request.executeQuery(requestUrl=requestUrl)
    for item in data['d']['results']:
        print "Item title: {0}".format(item["Title"])


def createListItem(url,ctxAuth):
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/lists/getbyTitle('{0}')/items".format(listTitle)   #Web resource endpoint

    print "Creating list item..."
    itemPayload = {'__metadata': { 'type': 'SP.Data.TasksListItem' }, 'Title': 'New Task'}
    data = request.executeQuery(requestUrl=requestUrl,data=itemPayload)

    if 'error' in data:
        print "An error occured while creating list item: {0}".format(data['error']['message']['value'])
        return

    print "Task has been succesfully created"
    #for item in data['d']['results']:
    #    print "Item title: {0}".format(item["Title"])
        