import json

from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_site_url

if __name__ == '__main__':
    """Demonstrates how to construct and submit requests without model involved"""
    ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)

    request = RequestOptions("{0}/_api/web/".format(test_site_url))
    response = ctx.execute_request_direct(request)
    json = json.loads(response.content)
    web_title = json['d']['Title']
    print("Web title: {0}".format(web_title))
