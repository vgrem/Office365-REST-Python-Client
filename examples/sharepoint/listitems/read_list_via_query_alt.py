import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from tests import test_client_credentials, test_team_site_url


def print_progress(items_read):
    print("Items read: {0}".format(items_read))


def create_paged_query(page_size):
    qry = CamlQuery()
    qry.ViewXml = f"""
    <View Scope='RecursiveAll'>
       <Query></Query>
       <QueryOptions><QueryThrottleMode>Override</QueryThrottleMode></QueryOptions>
       <RowLimit Paged='TRUE'>{page_size}</RowLimit>
   </View>
   """
    return qry


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.lists.get_by_title("Contacts_Large")
list_qry = create_paged_query(50)
result = target_list.render_list_data(list_qry.ViewXml).execute_query()
data = json.loads(result.value)
rows = data.get("Row", [])
print(len(rows))
