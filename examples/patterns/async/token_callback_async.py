"""
Acquire access tokens with an async callback.

``with_access_token`` (Graph and SharePoint) accepts an ``async def``. The async
API awaits it on the event loop, so a token broker reached over async HTTP never
blocks the loop, and concurrent requests share a single refresh: the token is
acquired once (single-flight) and reused until it expires.

The token source below is an ``httpx.AsyncClient`` (install the extra)::

    pip install office365-rest-python-client[httpx]

Point ``TOKEN_BROKER_URL`` at your broker. It should answer with an OAuth token
response, e.g. ``{"access_token": "...", "token_type": "Bearer",
"expires_in": 3600}``.

Pass an ``async def`` (or a factory returning one) — a plain ``lambda`` wrapping a
coroutine is not detected as async and would be treated as a synchronous callback.

https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow
"""

import asyncio
import os

import httpx
from office365.graph_client import GraphClient

TOKEN_BROKER_URL = os.environ.get("TOKEN_BROKER_URL", "http://localhost:8080/token")


def make_token_callback(http: httpx.AsyncClient):
    """Return an ``async def`` that fetches a token from the broker."""

    async def token_callback() -> dict:
        response = await http.get(TOKEN_BROKER_URL)
        response.raise_for_status()
        return response.json()

    return token_callback


async def main() -> None:
    async with httpx.AsyncClient(timeout=10) as http:
        client = GraphClient(token_callback=make_token_callback(http))

        # The async API awaits the callback on the loop; a concurrent fan-out
        # shares one acquisition and then the cached token.
        users = await client.users.top(5).select(["id", "displayName"]).get().execute_query_async()
        for user in users:
            print(user.display_name)

        print(f"Fetched {len(users)} users")


asyncio.run(main())
