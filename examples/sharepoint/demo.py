import datetime

from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.camlQuery import CamlQuery
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

lib = ctx.web.lists.get_by_title("Documents")

# construct a query
caml_query = CamlQuery()
offset = datetime.datetime.now() - datetime.timedelta(minutes=15)
caml_query.ViewXml = """<View Scope='RecursiveAll'>
    <Query>
        <Where>
            <Geq>
                <FieldRef Name='Modified' />
                <Value IncludeTimeValue='True' StorageTZ='TRUE' Type='DateTime'>{0}</Value>
            </Geq>
        </Where>
    </Query>
    <RowLimit>5000</RowLimit>
</View>""".format(offset.isoformat() + 'Z')

items = lib.get_items(caml_query)
ctx.load(lib)
ctx.execute_query()

for item in items:
    print(item.properties['Modified'])

