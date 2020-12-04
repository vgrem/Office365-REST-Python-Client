from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(settings["url"]).with_credentials(
                                             UserCredential(settings.get('user_credentials').get('username'),
                                                            settings.get('user_credentials').get('password')))

web = ctx.web.get().execute_query()
print(web.properties["Url"])
