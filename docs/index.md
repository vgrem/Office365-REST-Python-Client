---
title: Overview
---

<div class="hero" markdown="1">

# Office 365 REST Python Client

A Python client for the **Microsoft 365 and SharePoint REST APIs** — typed
models, fluent queries, and **hundreds of ready-to-run examples** for Teams,
To-Do, Bookings, Entra ID, OneDrive, and SharePoint.

<div class="hero-actions" markdown="1">

[:fontawesome-solid-rocket: Get started](getting-started.md){ .md-button .md-button--primary }
[:material-book-open-page-variant: Browse products](products/index.md){ .md-button }

</div>

</div>

## What you get

- **Two clients, one library** — `ClientContext` for the SharePoint REST API,
  `GraphClient` for Microsoft Graph.
- **Fluent queries** — `.select()`, `.filter()`, `.expand()`, `.top()`,
  server-driven paging, and `get_all()` for entire collections.
- **Deferred execution** — chain calls and send them all in one round-trip with
  `execute_query()`.
- **Async-ready** — every terminal has an `await ..._async()` twin, with no extra
  dependency required.
- **Ready-to-run examples** — every gallery script is a copy-paste starting
  point, organized by product.

## Reading path

| Page | What it's for |
|---|---|
| [Installation](installation.md) | `pip install` and requirements |
| [Upgrading from 2.x](upgrading.md) | the 3.0 property rename, and what else breaks |
| [Getting Started](getting-started.md) | pick your client, authenticate, first query |
| [Async / await](async.md) | run the same fluent API from `async` code |
| [Authentication](auth/index.md) | every auth flow, side by side |
| [Products](products/index.md) | the example gallery per Microsoft 365 service |
| [API Reference](api.md) | query patterns and power-user features |

New to Microsoft 365 APIs? Start with the [Microsoft Graph docs](https://learn.microsoft.com/en-us/graph/)
or the [SharePoint REST API reference](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api).
