"""
Returns a SharePoint List data
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

view_xml = """
<View>
    <Query>
        <Where>
        </Where>
    </Query>
     <ViewFields>
        <FieldRef Name='Title' />
        <FieldRef Name='Created' />
        <FieldRef Name='Author' />
    </ViewFields>
    <RowLimit>100</RowLimit>
</View>
"""


result = ctx.web.get_list_data_as_stream(
    "/Shared Documents", view_xml=view_xml
).execute_query()
print(result.value)
