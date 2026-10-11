"""
Load a SharePoint web asynchronously.

Builders stay synchronous; only the terminal call changes from
``execute_query()`` to ``await ...execute_query_async()``.

Requires delegated permission ``Sites.Read.All`` (certificate or username/password).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/web
"""

import asyncio

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def main() -> None:
    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    web = await ctx.web.get().execute_query_async()
    print(f"Web title: {web.title}")


asyncio.run(main())
