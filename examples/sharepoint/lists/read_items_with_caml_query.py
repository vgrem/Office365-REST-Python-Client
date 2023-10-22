import datetime

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def build_custom_query(page_size=100):
    """ "
    :type page_size: int
    """
    from_datetime = datetime.datetime(2022, 1, 20, 0, 0)
    qry = CamlQuery()
    qry.ViewXml = f"""
    <View Scope='RecursiveAll'>
       <Query>
           <Where>
              <Gt>
                 <FieldRef Name='Created'/>
                 <Value Type='DateTime' IncludeTimeValue='True'>{from_datetime.isoformat()}</Value>
              </Gt>
           </Where>
       </Query>
       <RowLimit Paged='TRUE'>{page_size}</RowLimit>
    </View>
    """
    return qry


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Site Pages"
site_pages = ctx.web.lists.get_by_title(list_title)
items = site_pages.get_items(build_custom_query(5)).execute_query()
print("Total items count: {0}".format(len(items)))
for index, item in enumerate(items):  # type: int, ListItem
    print("{0}: {1}".format(index, item.properties["Created"]))
