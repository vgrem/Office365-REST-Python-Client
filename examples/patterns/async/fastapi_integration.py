"""
Bridge the library into FastAPI/ASGI handlers without blocking the event loop.

The query builders are synchronous, but every terminal call has an async twin.
Inside an ASGI handler that means you simply ``await`` the terminal and let the
server keep serving other requests while Microsoft Graph or SharePoint is in
flight — no ``run_in_executor`` wrapper and no thread-pool tuning in your code.

The one rule that matters when many requests run at once: a context owns a single
pending-query queue, so never share one across handlers. The SharePoint endpoint
clones a shared, credentialed context per request; the Graph endpoint builds a
fresh client per request (in production, cache the token and share a transport
instead).

Run it::

    pip install fastapi uvicorn
    uvicorn fastapi_integration:app --port 8000
    curl "http://localhost:8000/site/web"
    curl "http://localhost:8000/users?top=5"

Read permissions are required for the target resources (``User.Read.All`` and
read access to the site).

https://learn.microsoft.com/en-us/graph/api/user-list
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from office365.graph_client import GraphClient
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, password, site_url, tenant, username

app = FastAPI(title="office365 async bridge")

# One credentialed SharePoint context; each request clones it so handlers never
# share a pending-query queue while still reusing one token and connection pool.
_base_ctx = ClientContext(site_url).with_client_certificate(
    tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
)


@app.get("/site/web")
async def site_web() -> dict[str, Any]:
    """Load the web title/url, blocking neither the loop nor other requests."""
    ctx = _base_ctx.clone(site_url)
    web = await ctx.web.select(["Title", "Url"]).get().execute_query_async()
    return {"title": web.title, "url": web.url}


@app.get("/users")
async def list_users(top: int = Query(default=10, ge=1, le=100)) -> list[dict[str, Any]]:
    """Read users from Microsoft Graph, awaiting the terminal call in the handler."""
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        users = await client.users.top(top).select(["id", "displayName", "mail"]).get().execute_query_async()
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex)) from ex
    return [{"id": u.id, "display_name": u.display_name, "mail": u.mail} for u in users]
