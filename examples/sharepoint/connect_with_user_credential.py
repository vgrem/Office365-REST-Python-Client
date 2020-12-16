from settings import settings


from office365.sharepoint.client_context import ClientContext
ctx = ClientContext(settings["url"]).with_user_credentials(settings.get('user_credentials').get('username'),
                                                           settings.get('user_credentials').get('password'))

web = ctx.web.get().execute_query()
print(web.properties["Url"])
