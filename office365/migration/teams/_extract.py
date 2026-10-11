"""Read-side extraction helpers for the Teams archive adapters."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from office365.migration.teams.models import (
    AppRecord,
    ChannelRecord,
    MemberRecord,
    TabRecord,
    TeamRecord,
    TeamsExportOptions,
)


def iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value else None


def member_record(member) -> MemberRecord:
    roles = list(member.roles) if member.roles else []
    return MemberRecord(
        id=member.id,
        display_name=member.get_property("displayName"),
        email=member.get_property("email"),
        user_id=member.get_property("userId"),
        roles=roles,
    )


def tab_record(tab) -> TabRecord:
    app = tab.teams_app
    configuration = tab.configuration
    return TabRecord(
        id=tab.id,
        display_name=tab.get_property("displayName"),
        teams_app_id=app.id if app else None,
        configuration=configuration.to_json() if configuration else {},
    )


def app_record(app) -> AppRecord:
    definition = app.teams_app_definition
    return AppRecord(
        id=app.id,
        teams_app_id=definition.get_property("teamsAppId") if definition else None,
        display_name=definition.get_property("displayName") if definition else None,
    )


def channel_record(channel, options: TeamsExportOptions) -> ChannelRecord:
    include_members = options.include_members and options.include_channel_members
    members = [member_record(m) for m in channel.members.get().execute_query()] if include_members else []
    tabs = (
        [tab_record(t) for t in channel.tabs.expand(["teamsApp"]).get().execute_query()] if options.include_tabs else []
    )
    return ChannelRecord(
        id=channel.id,
        display_name=channel.get_property("displayName"),
        description=channel.get_property("description"),
        membership_type=channel.get_property("membershipType"),
        created_datetime=iso(channel.get_property("createdDateTime")),
        members=members,
        tabs=tabs,
    )


def read_team(client, team_id: str, options: TeamsExportOptions, channels=None) -> TeamRecord:
    """Read a team's structure (metadata, members, channels, tabs, apps)."""
    team = client.teams[team_id].get().execute_query()
    members = [member_record(m) for m in team.members.get().execute_query()] if options.include_members else []
    apps = (
        [app_record(a) for a in team.installed_apps.expand(["teamsAppDefinition"]).get().execute_query()]
        if options.include_apps
        else []
    )
    channels = channels if channels is not None else team.channels.get().execute_query()
    return TeamRecord(
        id=team.id,
        display_name=team.display_name,
        description=team.description,
        visibility=team.visibility.value if team.visibility else None,
        classification=team.classification,
        is_archived=team.is_archived,
        web_url=team.web_url,
        created_datetime=iso(team.properties.get("createdDateTime")),
        mail_nickname=team.properties.get("mailNickname"),
        members=members,
        apps=apps,
        channels=[channel_record(ch, options) for ch in channels],
    )


def channel_messages(channel) -> list:
    """Root messages plus their replies for a channel (entities, for content access)."""
    messages = list(channel.messages.get().execute_query())
    for message in list(messages):
        messages.extend(message.replies.get().execute_query())
    return messages


def message_to_record(message, channel_id: str) -> dict[str, Any]:
    record = dict(message.properties)
    record["channel_id"] = channel_id
    return record
