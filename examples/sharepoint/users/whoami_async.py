"""
Show the current SharePoint user (title, login, UPN, email) — async.

Any authenticated user. The only difference from ``whoami.py`` is that the
terminal call is awaited: ``await ctx.web.current_user.get().execute_query_async()``.
Builders stay synchronous; only the call that hits the network becomes a coroutine.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/user-rest-api
"""

import argparse
import asyncio

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


async def main() -> None:
    argparse.ArgumentParser(description="Show the current SharePoint user").parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    me = await ctx.web.current_user.get().execute_query_async()
    print(f"Title:     {me.title}")
    print(f"Login:     {me.login_name}")
    print(f"UPN:       {me.user_principal_name}")
    print(f"Email:     {me.email}")


if __name__ == "__main__":
    asyncio.run(main())
