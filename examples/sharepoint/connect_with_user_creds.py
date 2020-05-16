from office365.runtime.auth.UserCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings


ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team/",
                                             UserCredential(settings['user_credentials']['username'],
                                                            settings['user_credentials']['password']))

web = ctx.web
ctx.load(web)
ctx.execute_query()
print(web.properties["Url"])


