from office365.runtime.auth.UserCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings


def getMyDriveClient(tenant_name, user_principal_name, password):
    user_name = user_principal_name.split('@')[0]
    my_drive_url = "https://{0}-my.sharepoint.com/personal/{1}_{0}_onmicrosoft_com/".format(tenant_name, user_name)
    return ClientContext.connect_with_credentials(my_drive_url, UserCredential(user_principal_name, password))


if __name__ == '__main__':
    tenant_name = settings['tenant'].split('.')[0]
    password = settings['user_credentials']['password']
    username = settings['user_credentials']['username']

    client = getMyDriveClient(tenant_name, username, password)
    client.load(client.web)
    client.execute_query()
    print(client.web.properties['Url'])
