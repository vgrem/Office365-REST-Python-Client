from settings import settings

from office365.runtime.auth.client_credential import ClientCredential

site_url = settings.get('url')
credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))


# ctx = ListDataService(site_url)
# ctx = ClientContext(site_url).with_credentials(credentials)
# ctx.execute_query()
