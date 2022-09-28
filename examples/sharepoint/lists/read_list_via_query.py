import datetime

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def query_by_datetime(source_list, from_datetime, page_size=100):
    """
    :type source_list: office365.sharepoint.lists.list.List
    :type from_datetime: datetime.datetime
    :type page_size: int
    """

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
    return source_list.get_items(qry)


def query_by_datetime_alt(source_list, from_datetime):
    """
    :type source_list: office365.sharepoint.lists.list.List
    :type from_datetime: datetime.datetime
    """

    filter_text = "Created gt datetime'{0}'".format(from_datetime.isoformat())
    return source_list.items.filter(filter_text).get()


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Site Pages"
site_pages = ctx.web.lists.get_by_title(list_title)
from_dt = datetime.datetime(2022, 1, 20, 0, 0)
items = query_by_datetime(site_pages, from_dt).execute_query()
print("Loaded items count: {0}".format(len(items)))
for index, item in enumerate(items):  # type: int, ListItem
    print("{0}: {1}".format(index, item.properties['Created']))
