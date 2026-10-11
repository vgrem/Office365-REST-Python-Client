from __future__ import annotations

from dataclasses import dataclass, field

from office365.outlook.mail.item_body import ItemBody
from office365.runtime.client_value import ClientValue


@dataclass
class VirtualEventPresenterDetails(ClientValue):
    bio: ItemBody = field(default_factory=ItemBody)
    company: str | None = None
    jobTitle: str | None = None
    linkedInProfileWebUrl: str | None = None
    personalSiteWebUrl: str | None = None
    photo: bytes | None = None
    twitterProfileWebUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventPresenterDetails"
