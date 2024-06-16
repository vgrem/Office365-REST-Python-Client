"""
Demonstrates how to retrieve site groups along with users
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
site_groups = ctx.web.site_groups.expand(["Users"]).get().execute_query()
for g in site_groups:
    print("Group: {0}".format(g.login_name))
    for u in g.users:
        print("User: {0}".format(u.login_name))
