import json
from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext

if __name__ == '__main__':

    context_auth = AuthenticationContext(url=settings['url'])
    if context_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                           password=settings['user_credentials']['password']):

        """Read Web client object"""
        ctx = ClientContext(settings['url'], context_auth)
        options = RequestOptions("{0}/_api/web/".format(settings['url']))
        options.set_header('Accept', 'application/json')
        options.set_header('Content-Type', 'application/json')
        data = ctx.execute_request_direct(options)
        json = json.loads(data.content)
        web_title = json['Title']
        print("Web title: {0}".format(web_title))

    else:
        print(context_auth.get_last_error())
