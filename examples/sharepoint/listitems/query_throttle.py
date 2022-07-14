from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from tests import test_client_credentials, test_team_site_url


def create_paged_query(page_size):
    qry = CamlQuery()
    qry.ViewXml = f"""
       <View Scope='RecursiveAll'>
          <Query><Where><Neq><FieldRef Name=\"FullName\" /><Value Type=\"Text\">Travis Clayton</Value></Neq></Where></Query>
          <QueryOptions><QueryThrottleMode>Override</QueryThrottleMode></QueryOptions>
          <RowLimit Paged='TRUE'>{page_size}</RowLimit>
      </View>
      """
    return qry


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
large_list = ctx.web.lists.get_by_title("Contacts_Large")
items = large_list.get_items(create_paged_query(100)).execute_query()
print(items)
