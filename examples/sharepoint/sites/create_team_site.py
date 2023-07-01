"""
Creates Team site
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials, create_unique_name

alias = create_unique_name("teamsite")
title = "Team Site"
ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)

site = ctx.create_team_site(alias, title).execute_query()
print(site.url)

# cleanup: remove resource
site.delete_object().execute_query()
