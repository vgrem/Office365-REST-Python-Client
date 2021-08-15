import json

from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_site_url


def load_web_by_relative_url(client):
    """
    :type client: ClientContext
    """
    response = client.execute_request_direct("web")
    response.raise_for_status()
    return json.loads(response.content)


def load_web_by_absolute_url(client):
    """
    :type client: ClientContext
    """
    request = RequestOptions("{0}/_api/web/".format(test_site_url))
    response = client.execute_request_direct(request)
    response.raise_for_status()
    return json.loads(response.content)


if __name__ == '__main__':
    """Demonstrates how to construct and submit requests without model involved"""
    ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
    #json = load_web_by_relative_url(ctx)
    json = load_web_by_absolute_url(ctx)
    web_title = json['d']['Title']
    print("Web title: {0}".format(web_title))
