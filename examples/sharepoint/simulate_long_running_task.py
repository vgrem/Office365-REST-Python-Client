import time
from settings import settings
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext


def process_site(context):
    target_web = context.web
    target_web.set_property("Description", "DEV site").update().get().execute_query()
    print(target_web.url)


credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))
ctx = ClientContext(settings['url']).with_credentials(credentials)

if __name__ == '__main__':
    while 1:
        print(f"{time.ctime()}: Processing site")
        process_site(ctx)
        time.sleep(10)
