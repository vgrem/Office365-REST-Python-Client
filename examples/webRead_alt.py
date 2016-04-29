from client.runtime.client_request import ClientRequest



def readWeb(url,ctxAuth):
    "Read Web client object"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/"   #Web resource endpoint
    data = request.execute_query_direct(request_url=requestUrl)

    webTitle = data['d']['Title']
    print "Web title: {0}".format(webTitle)
        