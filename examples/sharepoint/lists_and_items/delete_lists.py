from xml.etree import ElementTree
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


def is_custom_list(list_object):
    xml = ElementTree.fromstring(list_object.properties["SchemaXml"])
    scope_id = xml.attrib['ScopeId']
    return True


lists = ctx.web.lists.select(["Title", "SchemaXml"]).top(10).get().execute_query()
lists_to_delete = [l for l in lists if is_custom_list(l)]
for list_obj in lists_to_delete:  # type: List
    print(f"Deleting list .. {list_obj.title}")
    # list_obj.delete_object().execute_query()
