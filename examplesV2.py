from client.auth.AuthenticationContext import AuthenticationContext
from client.ClientContext import ClientContext
from settings import settings


if __name__ == '__main__':    
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquireTokenForUser(username=settings['username'], password=settings['password']):                  
        ctx = ClientContext(settings['url'],ctxAuth)
        web = ctx.Web
        ctx.load(web)
        ctx.executeQuery()

        print "Web site title: {0}".format(web.Properties['Title'])
    else:
        print ctxAuth.getLastErrorMessage()