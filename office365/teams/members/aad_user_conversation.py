from __future__ import annotations

from typing import Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.members.conversation import ConversationMember


class AadUserConversationMember(ConversationMember):
    """Represents an Azure Active Directory user in a team, a channel, or a chat."""

    @property
    def user_id(self) -> str | None:
        """The guid of the user."""
        return self.properties.get("userId")

    @property
    def user(self):
        from office365.directory.users.user import User

        return self.properties.get("user", User(self.context, ResourcePath("user", self.resource_path)))

    def to_json(self, json_format=None):
        return {
            "@odata.type": "#" + self.entity_type_name,
            "roles": self.roles.to_json(json_format),
            "user@odata.bind": f"{self.context.users.resource_url}/{self.user_id}",
        }

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AadUserConversationMember"
