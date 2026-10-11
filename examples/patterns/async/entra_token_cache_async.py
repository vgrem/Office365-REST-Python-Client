"""
Cache Entra ID access tokens across runs so repeat calls skip re-authentication.

``GraphClient`` accepts an MSAL ``SerializableTokenCache``; serialize it after a
run and deserialize it next time, and the next process reuses the refresh token
instead of prompting or redoing a full token exchange. That matters for services
that start often — the silent path avoids an interactive prompt and cuts the
per-start latency. Keep the cache file secret: it contains refresh tokens.

Requires delegated permission ``User.Read`` and a username + password (or another
interactive flow) so a refresh token is actually issued.

https://learn.microsoft.com/en-us/entra/identity-platform/msal-token-cache
https://learn.microsoft.com/en-us/graph/api/user-get
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import msal
from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def load_cache(cache_path: Path) -> tuple[msal.SerializableTokenCache, bool]:
    """Read the cache file on the calling thread (a few KB, once per run)."""
    cache = msal.SerializableTokenCache()
    loaded = cache_path.exists()
    if loaded:
        cache.deserialize(cache_path.read_text())
    return cache, loaded


def save_cache(cache_path: Path, cache: msal.SerializableTokenCache) -> bool:
    """Persist the cache if MSAL changed it; return whether it was written."""
    if not cache.has_state_changed:
        return False
    cache_path.write_text(cache.serialize())
    return True


async def main() -> None:
    parser = argparse.ArgumentParser(description="Reuse an MSAL token cache across runs")
    parser.add_argument("--cache", default="msal_cache.bin", help="token cache file")
    args = parser.parse_args()
    cache_path = Path(args.cache)

    cache, loaded = load_cache(cache_path)
    if loaded:
        print(f"Loaded token cache from {cache_path}")

    client = GraphClient(tenant=tenant, token_cache=cache).with_username_and_password(client_id, username, password)
    try:
        async with client:
            me = await client.me.select(["displayName", "userPrincipalName"]).get().execute_query_async()
            print(f"Signed in as {me.display_name} <{me.user_principal_name}>")
    finally:
        if save_cache(cache_path, cache):
            print(f"Saved token cache to {cache_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
