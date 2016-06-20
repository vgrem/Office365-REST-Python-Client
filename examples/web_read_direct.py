from client.runtime.auth.authentication_context import AuthenticationContext
from client.runtime.client_request import ClientRequest
from settings import settings

if __name__ == '__main__':
    context_auth = AuthenticationContext(url=settings['url'])
    if context_auth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        """Read Web client object"""
        request = ClientRequest(settings['url'], context_auth)
        request_url = "{0}/_api/web/".format(settings['url'])
        data = request.execute_query_direct(request_url=request_url)
        web_title = data['d']['Title']
        print "Web title: {0}".format(web_title)

    else:
        print context_auth.get_last_error()
