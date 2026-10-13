"""
Export all modern site pages to HTML files (text content only).

Reads each page and writes its title plus canvas content (the raw HTML in the
``CanvasContent1`` field, exposed as ``canvas_content``) to a local .html file.
Files, images, and videos embedded in the pages are not exported.

Uses offset paging: the site pages endpoint does not return a server-side next
link, so ``get_all()``/``paged()`` fall back to client-driven offset requests
automatically.

A Python port of PnP's ``spo-export-page-html`` script sample:
https://github.com/pnp/script-samples/tree/main/scripts/spo-export-page-html

https://learn.microsoft.com/en-us/sharepoint/dev/apis/site-pages-api-reference
"""

import argparse
import tempfile
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

PAGE_SIZE = 50


def main():
    parser = argparse.ArgumentParser(description="Export modern site pages to HTML files")
    parser.add_argument("--site-url", default=site_url, help="site URL")
    parser.add_argument(
        "--output",
        default=str(Path(tempfile.gettempdir()) / "site_pages"),
        help="output directory for the .html files (default: temp dir)",
    )
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    pages = list(ctx.site_pages.pages.paged(PAGE_SIZE).get().execute_query())
    pages = [page for page in pages if page.file_name and page.file_name.endswith(".aspx")]
    if not pages:
        print("No modern pages found.")
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        title = page.properties.get("Title") or ""
        content = page.canvas_content or ""
        filename = (page.file_name or "page").replace(".aspx", ".html")
        html = f"<div><h1>{title}</h1></div>{content}"
        (out_dir / filename).write_text(html, encoding="utf-8")
        print(f"  ✓ {filename}")

    print(f"\nExported {len(pages)} page(s) to {out_dir}")


if __name__ == "__main__":
    main()
