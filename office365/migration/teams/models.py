"""Serializable records for a Teams export archive."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MemberRecord:
    id: str | None = None
    display_name: str | None = None
    email: str | None = None
    user_id: str | None = None
    roles: list[str] = field(default_factory=list)


@dataclass
class TabRecord:
    id: str | None = None
    display_name: str | None = None
    teams_app_id: str | None = None
    configuration: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppRecord:
    id: str | None = None
    teams_app_id: str | None = None
    display_name: str | None = None


@dataclass
class ChannelRecord:
    id: str | None = None
    display_name: str | None = None
    description: str | None = None
    membership_type: str | None = None
    created_datetime: str | None = None
    members: list[MemberRecord] = field(default_factory=list)
    tabs: list[TabRecord] = field(default_factory=list)
    message_count: int = 0


@dataclass
class TeamRecord:
    id: str | None = None
    display_name: str | None = None
    description: str | None = None
    visibility: str | None = None
    classification: str | None = None
    is_archived: bool | None = None
    web_url: str | None = None
    created_datetime: str | None = None
    mail_nickname: str | None = None
    members: list[MemberRecord] = field(default_factory=list)
    apps: list[AppRecord] = field(default_factory=list)
    channels: list[ChannelRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TeamsExportOptions:
    """What to include in a Teams export archive."""

    include_members: bool = True
    include_channel_members: bool = True
    include_tabs: bool = True
    include_apps: bool = True
    include_messages: bool = True
    include_files: bool = False
    include_hosted_contents: bool = True
