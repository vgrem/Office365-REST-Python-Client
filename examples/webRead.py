from client.AuthenticationContext import AuthenticationContext
from client.ClientRequest import ClientRequest



def readWeb(url,ctxAuth):
    "Read Web client object"
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/"   #Web resource endpoint
    data = request.executeQuery(requestUrl=requestUrl)

    webTitle = data['d']['Title']
    print "Web title: {0}".format(webTitle)
        