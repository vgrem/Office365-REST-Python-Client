"""
Demonstrates how to construct and submit requests without model involved
"""

import json

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

if __name__ == "__main__":
    client = ClientContext(test_site_url).with_credentials(test_user_credentials)
    response = client.execute_request_direct("web")
    response.raise_for_status()
    json = json.loads(response.content)
    web_title = json["d"]["Title"]
    print("Web title: {0}".format(web_title))
