"""
Run several SharePoint queries concurrently.

A context drains its pending queue on every call, so independent requests are
overlapped by giving each one its own cloned context (which shares the
credentials and HTTP connection pool) and awaiting them together.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/web
"""

import asyncio

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def main() -> None:
    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    web_ctx = ctx.clone(site_url)
    lists_ctx = ctx.clone(site_url)

    web, lists = await asyncio.gather(
        web_ctx.web.get().execute_query_async(),
        lists_ctx.web.lists.get().execute_query_async(),
    )
    print(f"Web title: {web.title}")
    print(f"Lists: {len(lists)}")


asyncio.run(main())
