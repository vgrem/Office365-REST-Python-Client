"""
Demonstrates how to construct and submit requests without model involved
"""

import json

from office365.sharepoint.request import SharePointRequest
from tests import test_site_url, test_user_credentials

if __name__ == "__main__":
    request = SharePointRequest(test_site_url).with_credentials(test_user_credentials)
    response = request.execute_request("web")
    json = json.loads(response.content)
    web_title = json["d"]["Title"]
    print("Web title: {0}".format(web_title))
