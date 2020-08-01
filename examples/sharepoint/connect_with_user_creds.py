from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(settings["url"]).with_credentials(
                                             UserCredential(settings['user_credentials']['username'],
                                                            settings['user_credentials']['password']))

web = ctx.web
ctx.load(web)
ctx.execute_query()
print(web.properties["Url"])
