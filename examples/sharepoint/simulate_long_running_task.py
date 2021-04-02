import time
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials


def process_site(context):
    target_web = context.web
    target_web.set_property("Description", "DEV site").update().get().execute_query()
    print(target_web.url)


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

if __name__ == '__main__':
    while 1:
        print(f"{time.ctime()}: Processing site")
        process_site(ctx)
        time.sleep(10)
