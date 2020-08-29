from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.listdatasvc.list_data_service import ListDataService
from settings import settings

site_url = settings.get('url')
credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))


def create_folder():
    pass


#ctx = ListDataService(site_url)
#ctx = ClientContext(site_url).with_credentials(credentials)
#ctx.execute_query()
