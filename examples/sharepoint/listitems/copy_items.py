from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials, test_site_url

source_site_url = test_site_url
target_site_url = test_team_site_url

source_ctx = ClientContext(source_site_url).with_credentials(test_client_credentials)
source_items = source_ctx.web.lists.get_by_title("Tasks").items.get().top(10).execute_query()

target_ctx = ClientContext(target_site_url).with_credentials(test_client_credentials)
target_list = target_ctx.web.lists.get_by_title("Tasks")
for source_item in source_items:
    props = {k: v for k, v in source_item.properties.items() if k not in ['PredecessorsId', 'Id', 'ID']}
    target_list.add_item(props).execute_query()
