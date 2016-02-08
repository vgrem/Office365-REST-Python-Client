from lib.AuthenticationContext import AuthenticationContext
from lib.ClientRequest import ClientRequest
from settings import settings
from examples.webRead import readWeb
from examples.ListItemsOperations import readListItems, createListItem


if __name__ == '__main__':
    ctxAuth = AuthenticationContext(url=settings['url'])
    if ctxAuth.acquireTokenForUser(username=settings['username'], password=settings['password']):                  
        readWeb(settings['url'],ctxAuth)
        #readListItems(settings['url'],ctxAuth)
        #createListItem(settings['url'],ctxAuth)
    else:
        print ctxAuth.getLastErrorMessage()

    
    
   