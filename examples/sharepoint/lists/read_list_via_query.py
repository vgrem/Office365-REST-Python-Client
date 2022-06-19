from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def create_paged_query(page_size):
    qry = CamlQuery()
    qry.ViewXml = f"""
    <View Scope='RecursiveAll'>
       <Query></Query>
       <RowLimit Paged='TRUE'>{page_size}</RowLimit>
   </View>
   """
    return qry


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.lists.get_by_title("Contacts_Large")
list_qry = create_paged_query(50)
items = target_list.get_items(list_qry).execute_query()
print("Loaded items count: {0}".format(len(items)))
for index, item in enumerate(items):  # type: int, ListItem
    print("{0}: {1}".format(index, item.properties['Title']))
