# example that parses document library with name "Software" and prints content of each folder in it (only two levels of
# file tree). Current example uses App authentication. See examples "connect_with_app.py"
# for detailed info read official Microsoft article: Granting access using SharePoint App-Only

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

site_url="https://company.sharepoint.com/sites/team-name"

app_principal = {
    'client_id': 'client id',
    'client_secret': 'client secret',
}

context_auth = AuthenticationContext(url=site_url)
context_auth.acquire_token_for_app(client_id=app_principal['client_id'], client_secret=app_principal['client_secret'])

ctx = ClientContext(site_url, context_auth)
source_folder = ctx.web.lists.get_by_title("Software").rootFolder

folders = source_folder.folders
ctx.load(folders)
ctx.execute_query()

for folder in folders:
    print(folder.properties["ServerRelativeUrl"])
    files = folder.files
    ctx.load(files)
    ctx.execute_query()
    for file in files:
        print("File name: {}, Size: {:.2f} Mb".format(file.properties["Name"], int(file.properties["Length"]) / 2**20))

    folders_second_lvl = folder.folders
    ctx.load(folders_second_lvl)
    ctx.execute_query()
    for folder_second_lvl in folders_second_lvl:
        print("Folder name: " + folder_second_lvl.properties["Name"])

    print("\n\n")
