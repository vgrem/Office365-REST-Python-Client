from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import requests
from typing_extensions import Self

from office365.directory.groups.collection import GroupCollection
from office365.directory.groups.group import Group
from office365.entity_collection import EntityCollection
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.builder import ODataPathBuilder
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.exceptions import NotFoundException
from office365.teams.chats.messages.collection import ChatMessageCollection
from office365.teams.operations.async_operation import TeamsAsyncOperation, wait_for_operation
from office365.teams.team import Team

if TYPE_CHECKING:
    from office365.runtime.operations import ProgressCallback


class TeamCollection(EntityCollection[Team]):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Team, resource_path)

    def get_all(
        self,
        page_size: int | None = None,
        page_loaded: Callable[[Any], None] | None = None,
        progress: "ProgressCallback | None" = None,
        dedupe_by: str | None = None,
    ) -> Self:
        """List all teams in Microsoft Teams for an organization"""

        def _init_teams(groups: GroupCollection) -> None:
            for grp in groups:
                team = Team(self.context, ResourcePath(grp.id, self.resource_path))
                team.copy_from(grp)
                self.add_child(team)
            if callable(page_loaded):
                page_loaded(self)

        self.context.groups.filter("resourceProvisioningOptions/Any(x:x eq 'Team')").get_all(
            page_size, page_loaded=_init_teams, progress=progress, dedupe_by=dedupe_by
        )
        return self

    def find_by_name(self, display_name: str, *, required: bool = False) -> Team:
        """Look up a team by its ``displayName``.

        A team is backed by a Microsoft 365 group and ``GET /teams`` does not
        support ``$filter``, so the lookup goes through
        ``GET /groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team') and displayName eq '...'``
        — the approach Microsoft documents for listing teams. Deferred — run
        with ``execute_query()``; the returned team is left uninitialized when
        no team has that name (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead.

        Args:
            display_name (str): The team (group) display name
            required (bool): Raise ``NotFoundException`` on a miss when ``True``
        """
        return_type = Team(self.context)
        self.add_child(return_type)

        expression = (
            f"resourceProvisioningOptions/Any(x:x eq 'Team') and displayName eq '{escape_odata_string(display_name)}'"
        )
        group = self.context.groups.first_or_none(expression)

        def _populate(group: Group) -> None:
            # copy_from sets the id property, which anchors the team's resource
            # path at /teams/{id} (see Entity.set_property).
            if group.is_loaded:
                return_type.copy_from(group)
            elif required:
                raise NotFoundException(return_type, expression)

        group.after_execute(_populate)
        return return_type

    def get_all_messages(self) -> ChatMessageCollection:
        """Export every channel message across all teams (``GET /teams/getAllMessages``).

        Application-only (``Teamwork.Migrate.All``). Deferred — run with
        ``execute_query()``.

        Chain ``.filter(...)``/``.select(...)``/``.top(...)`` on the returned
        collection to shape the request.
        """
        return_type = ChatMessageCollection(self.context, self.resource_path)
        qry = FunctionQuery(self, "getAllMessages", None, return_type)
        self.context.add_query(qry)
        return return_type

    def _create_payload(
        self,
        display_name: str,
        description: str | None,
        template: str,
        owners: list[str] | None,
    ) -> dict:
        """Build the ``POST /teams`` body, including owners when supplied.

        Application-context creation must name at least one owner, so pass the
        user ids (or user principal names) of the intended owners.
        """
        payload: dict = {
            "displayName": display_name,
            "description": description,
            "template@odata.bind": f"{self.context.teams_templates.resource_url}('{template}')",
        }
        if owners:
            payload["members"] = [
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"{self.context.users.resource_url}('{owner}')",
                }
                for owner in owners
            ]
        return payload

    def create(
        self,
        display_name: str,
        description: str | None = None,
        template: str = "standard",
        owners: list[str] | None = None,
    ) -> TeamsAsyncOperation:
        """Create a new team (async) — returns the ``teamsAsyncOperation``.

        The operation is submitted on ``execute_query()`` (HTTP 202). Poll the
        returned operation (:meth:`TeamsAsyncOperation.poll_for_status`) to wait
        for provisioning; ``target_resource_id`` then holds the team id. Use
        :meth:`create_and_wait` for the convenience path that returns a ready
        team.

        Args:
            display_name (str): The name of the team.
            description (str or None): An optional description for the team. Maximum length: 1024 characters.
            template (str): The team template to create from (default ``"standard"``).
            owners (list[str] or None): User ids or user principal names to assign as owners.
                Required when creating in application context.
        """
        return_type = TeamsAsyncOperation(self.context, EntityPath(None, self.resource_path))

        def _process_response(resp: requests.Response) -> None:
            loc = resp.headers.get("Location")
            if loc is not None:
                operation_path = ODataPathBuilder.parse_url(loc)
                return_type._resource_path = operation_path

        payload = self._create_payload(display_name, description, template, owners)
        qry = CreateEntityQuery(self, payload, return_type)
        self.context.add_query(qry).after_execute(_process_response, include_response=True)
        return return_type

    def create_and_wait(
        self,
        display_name: str,
        description: str | None = None,
        template: str = "standard",
        owners: list[str] | None = None,
    ) -> Team:
        """Create a team and wait for provisioning (deferred).

        Chains the async creation, the ``teamsAsyncOperation`` poll, and a full
        team ``GET`` through ``after_execute`` hooks — one ``execute_query()``
        returns a provisioned :class:`Team` with its properties loaded.

        Args:
            display_name (str): The name of the team.
            description (str or None): An optional description for the team. Maximum length: 1024 characters.
            template (str): The team template to create from (default ``"standard"``).
            owners (list[str] or None): User ids or user principal names to assign as owners.
                Required when creating in application context.
        """
        return_type = Team(self.context)
        self.add_child(return_type)

        def _process_response(resp: requests.Response) -> None:
            content_loc = resp.headers.get("Content-Location")
            assert content_loc is not None
            team_path = ODataPathBuilder.parse_url(content_loc)
            return_type.set_property("id", team_path.segment, False)

            loc = resp.headers.get("Location")
            assert loc is not None
            operation = TeamsAsyncOperation(self.context, ODataPathBuilder.parse_url(loc))

            def _on_succeeded(_op) -> None:
                return_type.get()  # queue a full GET to load the team's properties

            wait_for_operation(operation, success_callback=_on_succeeded)

        payload = self._create_payload(display_name, description, template, owners)
        qry = CreateEntityQuery(self, payload, return_type)
        self.context.add_query(qry).after_execute(_process_response, include_response=True)
        return return_type
