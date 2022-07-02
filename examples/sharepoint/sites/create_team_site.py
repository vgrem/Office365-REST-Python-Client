from random import randint

from office365.sharepoint.sites.site import Site
from tests import test_site_url, test_user_credentials


alias = str(randint(0, 10000))
title = "Team Site"
site = Site.create_team_site(test_site_url, alias, title).with_credentials(test_user_credentials).execute_query()
print(site.url)
