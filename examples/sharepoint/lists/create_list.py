from random import randint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_name = "Tasks" + str(randint(0, 10000))
create_info = ListCreationInformation(list_name, None, ListTemplateType.Tasks)
list_object = ctx.web.lists.add(create_info).execute_query()
print("List has been created: {0}".format(list_object.title))
