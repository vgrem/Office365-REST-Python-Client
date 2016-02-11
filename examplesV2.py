from client.auth.AuthenticationContext import AuthenticationContext
from client.ClientContext import ClientContext
from settings import settings


def loadWeb(ctx):
     web = ctx.Web
     ctx.load(web)
     ctx.executeQuery()
     print "Web site url: {0}".format(web.Properties['ServerRelativeUrl'])
     return web 

def updateWeb(web):
     web.Properties['Title'] = "New web site"
     web.update()
     web.Context.executeQuery()
     print "Web site has been updated"

def createWeb(ctx):
     creationInfo = {} 
     creationInfo['Url'] = "projectnews" 
     creationInfo['Title'] = "Project News" 
     newWeb = ctx.Web.Webs.add(creationInfo) 
     ctx.executeQuery() 
     print "Web site {0} has been created".format(newWeb.Properties['Title'])


def deleteWeb(web):
     web.deleteObject() 
     web.Context.executeQuery() 
     print "Web site has been deleted"


if __name__ == '__main__':    
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquireTokenForUser(username=settings['username'], password=settings['password']):                  
        ctx = ClientContext(settings['url'],ctxAuth)
        #web = createWeb(ctx)
        web = loadWeb(ctx)
        #updateWeb(ctx.Web)
        deleteWeb(web)
    else:
        print ctxAuth.getLastErrorMessage()