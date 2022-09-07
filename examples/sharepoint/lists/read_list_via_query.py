from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def create_paged_query(page_size):
    """
    :type page_size: int
    """

    qry = CamlQuery()
    qry.ViewXml = f"""
    <View Scope='RecursiveAll'>
       <Query>
           <Where><Geq><FieldRef Name='Created'/><Value Type='DateTime' IncludeTimeValue='False'>2020-05-10T18:59:10Z</Value></Geq></Where>
       </Query>
       <ViewFields>
            <FieldRef Name='Title' />
       </ViewFields>
       <RowLimit Paged='TRUE'>{page_size}</RowLimit>
   </View>
   """
    return qry

# 2020-03-20T14:30:43
ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.lists.get_by_title("Contacts_Large")
list_qry = create_paged_query(50)
items = target_list.get_items(list_qry).execute_query()
print("Loaded items count: {0}".format(len(items)))
for index, item in enumerate(items):  # type: int, ListItem
    print("{0}: {1}".format(index, item.properties['Created']))
