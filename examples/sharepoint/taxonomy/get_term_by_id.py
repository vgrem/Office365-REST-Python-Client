"""
Gets a term by its GUID from the site's TaxonomyHiddenList.

The hidden list is populated lazily as content is tagged with a term, so a
term that has never been used may not appear here yet.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/taxonomy
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Get a taxonomy term by its GUID")
    parser.add_argument(
        "--term-id",
        default="aa93c464-92b6-4773-8d30-c37e5003755d",
        help="GUID of the term to look up",
    )
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    taxonomy_list = ctx.web.lists.get_by_title("TaxonomyHiddenList")
    item = taxonomy_list.items.first_or_none(f"IdForTerm eq '{args.term_id}'").execute_query()
    if item.is_loaded:
        print(item.properties.get("Title"))
    else:
        print(f"Term not found in TaxonomyHiddenList: {args.term_id}")
        print("Hint: the hidden list is populated lazily as content is tagged with the term.")


if __name__ == "__main__":
    main()
