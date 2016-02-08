from lib.AuthenticationContext import AuthenticationContext
from lib.ClientRequest import ClientRequest

def readWeb(url,ctxAuth):
    request = ClientRequest(url,ctxAuth)
    requestUrl = "/_api/web/"   #Web resource endpoint
    data = request.executeQuery(requestUrl=requestUrl)

    webTitle = data['d']['Title']
    print "Web title: {0}".format(webTitle)
        