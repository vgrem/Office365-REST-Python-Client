"""Read list items using a CAML query.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse
import datetime

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def build_custom_query(since: datetime.datetime, page_size: int = 100) -> CamlQuery:
    """A CAML view that only returns items created after ``since``."""
    query = CamlQuery()
    query.ViewXml = f"""
    <View Scope='RecursiveAll'>
       <Query>
           <Where>
              <Gt>
                 <FieldRef Name='Created'/>
                 <Value Type='DateTime' IncludeTimeValue='True'>{since.isoformat()}</Value>
              </Gt>
           </Where>
       </Query>
       <RowLimit Paged='TRUE'>{page_size}</RowLimit>
    </View>
    """
    return query


def main():
    parser = argparse.ArgumentParser(description="Read list items using a CAML query")
    parser.add_argument("--list-title", default="Site Pages", help="list title")
    parser.add_argument("--since", default="2022-01-20", help="only items created after this date")
    parser.add_argument("--page-size", type=int, default=5, help="CAML row limit per page")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    since = datetime.datetime.fromisoformat(args.since)
    items = (
        ctx.web.lists.get_by_title(args.list_title).get_items(build_custom_query(since, args.page_size)).execute_query()
    )
    print(f"Total items count: {len(items)}")
    for index, item in enumerate(items):
        print(f"  {index}: {item.properties['Created']}")


if __name__ == "__main__":
    main()
