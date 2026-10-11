"""
List rooms and room lists, and how to invite one.

Rooms and room lists come from the **places** API (``Place.Read.All``). A room has
an email address, so it is invited to a meeting exactly like an attendee — which
is how you book a physical room.

Requires delegated permission ``Place.Read.All``.

https://learn.microsoft.com/en-us/graph/api/resources/place
https://learn.microsoft.com/en-us/graph/api/place-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    argparse.ArgumentParser(description="List rooms and room lists").parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    rooms = client.places.rooms.get().execute_query()
    print(f"Rooms ({len(rooms)}):")
    for room in rooms:
        print(
            f"  {room.display_name:30}  {room.email_address or '-':30}  "
            f"capacity={room.capacity or '?'}  building={room.building or '-'}"
        )

    room_lists = client.places.room_lists.get().execute_query()
    print(f"\nRoom lists ({len(room_lists)}):")
    for room_list in room_lists:
        print(f"  {room_list.display_name:30}  {room_list.email_address or '-'}")

    if rooms:
        print(f"\nTo book a room, invite it as an attendee: {rooms[0].email_address}")


if __name__ == "__main__":
    main()
