"""
Return to automatic presence — the counterpart of ``set.py``.

Until you clear it, the preferred presence keeps overriding the status Teams
computes from your activity, and the status message keeps showing even after
your "meeting" is over.

Requires the delegated permission ``Presence.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/presence-clearuserpreferredpresence
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Clear your preferred presence")
    parser.add_argument(
        "--keep-message",
        action="store_true",
        help="clear only the presence, leave the status message alone",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    presence = client.me.presence

    presence.clear_user_preferred_presence().execute_query()
    print("Preferred presence cleared — presence is automatic again")

    if not args.keep_message:
        # There is no clearStatusMessage action in this API version, so an empty
        # message is used as the equivalent of "no status message".
        presence.set_status_message(message="").execute_query()
        print("Status message cleared")


if __name__ == "__main__":
    main()
