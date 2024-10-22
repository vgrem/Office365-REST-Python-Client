"""
Demonstrates how to construct and submit requests without model involved
"""

import json

from office365.sharepoint.request import SharePointRequest
from tests import test_site_url, test_user_credentials

request = SharePointRequest(test_site_url).with_credentials(test_user_credentials)

try:
    response = request.execute_request("web/currentUser")
    json = json.loads(response.content)
    prop_val = json["d"]["UserPrincipalName"]
    print("UserPrincipalName: {0}".format(prop_val))
except Exception as e:
    print("An error occurred: {0}".format(e))
