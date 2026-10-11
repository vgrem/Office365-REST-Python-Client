from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.intune.servicecommunications.health.posttype import PostType
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.client_value import ClientValue


@dataclass
class ServiceHealthIssuePost(ClientValue):
    createdDateTime: datetime | None = None
    description: ItemBody = field(default_factory=ItemBody)
    postType: PostType = PostType.regular

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceHealthIssuePost"
