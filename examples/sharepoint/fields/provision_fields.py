"""
Provision multiple typed fields on a list from a schema specification.

Declares each column as a FieldCreationInformation — so rich types such as
Choice can carry their choices — and ensures them all in one deferred pass.
Re-running is a no-op: existing columns are reused (or reconciled with
``on_conflict="update"``).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

LIST_TITLE = "Tasks"
FIELDS = [
    FieldCreationInformation(Title="CustomerName", FieldTypeKind=FieldType.Text),
    FieldCreationInformation(Title="Quantity", FieldTypeKind=FieldType.Number),
    FieldCreationInformation(Title="DueDate", FieldTypeKind=FieldType.DateTime),
    FieldCreationInformation(
        Title="Status",
        FieldTypeKind=FieldType.Choice,
        Choices=["Not Started", "In Progress", "Completed", "Deferred"],
    ),
    FieldCreationInformation(Title="Notes", FieldTypeKind=FieldType.Note),
]


def main():
    parser = argparse.ArgumentParser(description="Provision typed fields from a schema spec")
    parser.add_argument("--list-title", default=LIST_TITLE, help="Target list")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lst = ctx.web.lists.ensure_list(args.list_title)

    fields = lst.ensure_fields(FIELDS)
    ctx.execute_query()
    for info, field in zip(FIELDS, fields):
        print(f"  created {info.Title:16s} ({info.FieldTypeKind.name}) -> {field.internal_name}")


if __name__ == "__main__":
    main()
