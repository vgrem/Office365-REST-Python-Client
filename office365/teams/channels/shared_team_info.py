from typing import Optional

from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.info import TeamInfo
from office365.teams.members.conversation import ConversationMember


class SharedWithChannelTeamInfo(TeamInfo):
    """Represents information for a team with which a channel is shared. A team can be shared multiple channels."""

    @property
    def is_host_team(self) -> Optional[bool]:
        """Indicates whether the team is the host of the channel."""
        return self.properties.get("isHostTeam", None)

    @property
    def allowed_members(self) -> EntityCollection[ConversationMember]:
        """A collection of team members who have access to the shared channel."""
        return self.properties.get(
            "allowedMembers",
            EntityCollection(
                self.context,
                ConversationMember,
                ResourcePath("allowedMembers", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        # The base TeamInfo serializes as "teamInfo"; the sharedWithTeams endpoint
        # rejects anything but the concrete sharedWithChannelTeamInfo type.
        return "microsoft.graph.sharedWithChannelTeamInfo"
