"""
Creates a list item and uploads an attachment
"""

import argparse
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Create a list item and upload an attachment")
    parser.add_argument("--list-title", default="Company Tasks", help="list title")
    parser.add_argument("--title", default="New Task", help="new list item title")
    parser.add_argument(
        "--file",
        default=str(Path(__file__).resolve().parents[3] / "data" / "Financial Sample.xlsx"),
        help="file to upload as an attachment",
    )
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant,
        client_id=client_id,
        username=username,
        password=password,
    )
    tasks_list = ctx.web.lists.get_by_title(args.list_title)

    # 1. create a new list item
    task_item = tasks_list.add_item({"Title": args.title}).execute_query()

    # 2. read & upload attachment for a list item
    with open(args.file, "rb") as f:
        attachment = task_item.attachment_files.upload(f).execute_query()
    print(attachment)


if __name__ == "__main__":
    main()
