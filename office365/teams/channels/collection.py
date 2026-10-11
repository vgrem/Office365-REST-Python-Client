from __future__ import annotations

from http import HTTPStatus
from typing import Any

import requests

from office365.entity_collection import EntityCollection
from office365.runtime.paths.builder import ODataPathBuilder
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.teams.channels.channel import Channel
from office365.teams.chats.messages.collection import ChatMessageCollection
from office365.teams.operations.async_operation import TeamsAsyncOperation, wait_for_operation


class ChannelCollection(EntityCollection[Channel]):
    """Team's channel collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Channel, resource_path)

    def add(
        self,
        display_name: str,
        description: str | None = None,
        membership_type: str | None = None,
        owners: list[str] | None = None,
        **kwargs: Any,
    ) -> Channel:
        """Create a new channel in a Microsoft Team, as specified in the request body.

        Standard channels are created synchronously (the channel body is the
        response). Shared and private channels are provisioned asynchronously:
        the service answers ``202 Accepted`` with a Teams operation, so this
        method polls it and loads the finished channel through the same
        ``execute_query()`` call.

        Args:
            description (str): Optional textual description for the channel.
            display_name (str): Channel name as it will appear to the user in Microsoft Teams.
            membership_type (str): The type of the channel.
            owners (list[str] or None): User ids or user principal names to assign as the
                channel owners. Application context must name at least one owner when
                creating a shared (or private) channel.
        """
        payload: dict = {
            "displayName": display_name,
            "description": description,
            "membershipType": membership_type,
        }
        if owners:
            users_url = self.context.users.resource_url
            payload["members"] = [
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"{users_url}('{owner}')",
                }
                for owner in owners
            ]
        payload.update(kwargs)

        return_type = Channel(self.context, EntityPath(None, self.resource_path))
        self.add_child(return_type)

        def _process_response(resp: requests.Response) -> None:
            if resp.status_code != HTTPStatus.ACCEPTED:
                return
            location = resp.headers.get("Location")
            assert location is not None
            operation = TeamsAsyncOperation(self.context, ODataPathBuilder.parse_url(location))

            def _on_succeeded(op: TeamsAsyncOperation) -> None:
                # The operation's targetResourceId is the *team* id; the channel URL
                # (with the channel id) is in targetResourceLocation.
                location = op.target_resource_location
                assert location is not None
                return_type._resource_path = ODataPathBuilder.parse_url(location)
                return_type.get()  # queue a GET that loads the finished channel

            wait_for_operation(operation, success_callback=_on_succeeded)

        qry = CreateEntityQuery(self, payload, return_type)
        self.context.add_query(qry).after_execute(_process_response, include_response=True)
        return return_type

    def get_all_messages(self) -> ChatMessageCollection:
        """
        Retrieve messages across all channels in a team, including text, audio, and video conversations.

        Chain ``.filter(...)``/``.select(...)``/``.top(...)`` on the returned
        collection to shape the request.
        """
        return_type = ChatMessageCollection(self.context, self.resource_path)
        qry = FunctionQuery(self, "getAllMessages", None, return_type)
        self.context.add_query(qry)
        return return_type
