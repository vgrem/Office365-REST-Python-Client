from settings import settings

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

url = 'https://mediadev8.sharepoint.com/NewsArchive'
settings['client_credentials']['client_id'] = '82e32e70-f031-4978-9fcd-1233db95990f'
settings['client_credentials']['client_secret'] = '6rpUpc7O3M8loDFKE5H4auunS2geYL4Vs/pXUdjDSU0='

if __name__ == '__main__':
    context_auth = AuthenticationContext(url=url)
    if context_auth.acquire_token_for_app(client_id=settings['client_credentials']['client_id'],
                                          client_secret=settings['client_credentials']['client_secret']):
        ctx = ClientContext(url, context_auth)
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        print("Web title: {0}".format(web.properties['Title']))

    else:
        print(context_auth.get_last_error())
