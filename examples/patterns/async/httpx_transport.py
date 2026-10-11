"""
Use the optional native-async httpx transport.

Install the extra first::

    pip install office365-rest-python-client[httpx]

The synchronous path keeps using the default ``requests``-based transport; only
asynchronous calls go through httpx. Closing the async transport releases its
connection pool.

Requires delegated permission ``Sites.Read.All``.

https://www.python-httpx.org/
"""

import asyncio

from office365.runtime.transport.httpx_transport import HttpxTransport
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def main() -> None:
    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    ctx.pending_request().with_async_transport(HttpxTransport())
    try:
        web = await ctx.web.get().execute_query_async()
        print(f"Web title: {web.title}")
    finally:
        await ctx.pending_request().async_transport.aclose()


asyncio.run(main())
