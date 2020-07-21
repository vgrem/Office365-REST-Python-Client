import json

from office365.runtime.auth.userCredential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
from settings import settings

if __name__ == '__main__':
    """Demonstrates how to construct and submit requests without model involved"""
    ctx = ClientContext.connect_with_credentials(settings['url'],
                                                 UserCredential(settings['user_credentials']['username'],
                                                                settings['user_credentials']['password']))

    request = RequestOptions("{}/_api/web/".format(settings['url']))
    response = ctx.execute_request_direct(request)
    json = json.loads(response.content)
    web_title = json['d']['Title']
    print(f"Web title: {web_title}")
