"""
"""

import asyncio

from requests import Response

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url


async def do_work(client: ClientContext, instance: int):
    def _inspect_response(resp: Response):
        header_names = ["RateLimit-Limit", "RateLimit-Remaining", "RateLimit-Reset"]
        rate_limit = {}
        for header_name in header_names:
            header_value = resp.headers.get(header_name, None)
            if header_value is not None:
                rate_limit[header_name] = header_value

        if rate_limit:
            print(rate_limit)

    def _execute(iteration: int):
        web = client.web.get().execute_query_with_incremental_retry()
        if iteration % 25 == 0:
            print(
                "Instance #{0}, iteration: {1}, result: {2}".format(
                    instance, iteration, web.title
                )
            )

    for i in range(1000):
        await loop.run_in_executor(None, _execute, i)


async def main():
    ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
    tasks = []
    for i in range(20):
        tasks.append(do_work(ctx, i))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
