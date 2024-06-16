"""
Share a Web with user
"""

import sys

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.external_site_option import ExternalSharingSiteOption
from tests import (
    test_team_site_url,
    test_user_credentials,
    test_user_principal_name_alt,
)

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

result = ctx.web.share(
    test_user_principal_name_alt, ExternalSharingSiteOption.View
).execute_query()
if result.error_message is not None:
    sys.exit("Web sharing failed: {0}".format(result.error_message))

print(
    "Web '{0}' has been shared with user '{1}'".format(
        result.url, test_user_principal_name_alt
    )
)
