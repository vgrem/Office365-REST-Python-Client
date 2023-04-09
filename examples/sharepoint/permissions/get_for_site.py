from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.groups.group import Group
from office365.sharepoint.principal.users.user import User
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

site_groups = ctx.web.site_groups.expand(["Users"]).get().execute_query()
for g in site_groups:  # type: Group
    print("Group name: {0}".format(g.login_name))
    for u in g.users:  # type: User
        print("User name: {0}".format(u.login_name))
