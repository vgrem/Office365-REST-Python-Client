import time
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.server_settings import ServerSettings
from tests import test_site_url, test_client_credentials


def print_server_settings(context):
    """
    :type context: ClientContext
    """
    is_online = ServerSettings.is_sharepoint_online(context)
    installed_languages = ServerSettings.get_global_installed_languages(context, 15)
    context.execute_batch()
    print("Is SharePoint Online? : {0}".format(is_online.value))
    print("Installed languages amount : {0}".format(len(installed_languages.items)))


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

if __name__ == '__main__':
    start_time = time.time()
    while True:
        print(f" %s : Processing site..." % int(time.time() - start_time))
        print_server_settings(ctx)
        time.sleep(30)
