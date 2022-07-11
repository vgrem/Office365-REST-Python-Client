from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.onedrive.drives.drive import Drive


client = GraphClient(acquire_token_by_client_credentials)
drives = client.drives.get().top(10).execute_query()
for drive in drives:  # type: Drive
    print("Drive url: {0}".format(drive.web_url))
