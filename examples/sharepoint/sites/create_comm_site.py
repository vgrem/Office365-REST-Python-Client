from random import randint

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)

alias = str(randint(0, 10000))
title = "Communication Site"
site = ctx.create_communication_site(alias, title).execute_query()
print(site.url)
