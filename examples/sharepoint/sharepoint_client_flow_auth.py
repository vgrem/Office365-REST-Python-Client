import json

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_request import ClientRequest
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext

app_settings = {
    'url': 'https://contoso.sharepoint.com/',
    'client_id': '8efc226b-ba3b-4def-a195-4acdb8d20ca9',
    'client_secret': '',
}


if __name__ == '__main__':
    context_auth = AuthenticationContext(url=app_settings['url'])
    if context_auth.acquire_token_for_app(client_id=app_settings['client_id'], client_secret=app_settings['client_secret']):
        """Read Web client object"""
        ctx = ClientContext(app_settings['url'], context_auth)

        request = ClientRequest(ctx)
        options = RequestOptions("{0}/_api/web/".format(app_settings['url']))
        options.set_header('Accept', 'application/json')
        options.set_header('Content-Type', 'application/json')
        data = ctx.execute_request_direct(options)
        s = json.loads(data.content)
        web_title = s['Title']
        print("Web title: {0}".format(web_title))

    else:
        print(context_auth.get_last_error())



