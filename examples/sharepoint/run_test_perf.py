"""
Diagnosing performance issues

In SharePoint, you can access the information that is sent back to the client in the response header for each file.
The most useful value for diagnosing performance issues is SPRequestDuration, which displays the amount of time
that the request took on the server to be processed. This can help determine if the request is heavy and resource
intensive.

https://learn.microsoft.com/en-us/microsoft-365/enterprise/diagnosing-performance-issues-with-sharepoint-online?view=o365-worldwide
"""

from requests import Response

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url


def do_work(client: ClientContext):
    def _after_execute(resp: Response):
        header_name = "SPRequestDuration"
        duration = resp.headers.get(header_name, None)
        if duration:
            print("SPRequestDuration: {0}".format(duration))

    def _execute(iteration: int):
        web = (
            client.web.get()
            .after_execute(_after_execute, include_response=True)
            .execute_query()
        )
        print("Iteration: {0}, result: {1}".format(iteration, web.title))

    for i in range(10):
        _execute(i)


if __name__ == "__main__":
    ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
    do_work(ctx)
