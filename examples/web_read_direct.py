from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.runtime.client_request import ClientRequest
from client.office365.runtime.utilities.request_options import RequestOptions
from settings import settings
import json

if __name__ == '__main__':
    context_auth = AuthenticationContext(url=settings['url'])
    if context_auth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        """Read Web client object"""
        request = ClientRequest(settings['url'], context_auth)
        options = RequestOptions("{0}/_api/web/".format(settings['url']))
        options.set_header('Accept', 'application/json')
        options.set_header('Content-Type', 'application/json')
        data = request.execute_query_direct(options)
        s = json.loads(data.content)
        web_title = s['Title']
        print "Web title: " + web_title

    else:
        print context_auth.get_last_error()
