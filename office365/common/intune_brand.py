from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.mime_content import MimeContent
from office365.intune.devices.configurations.rgb_color import RgbColor
from office365.runtime.client_value import ClientValue


@dataclass
class IntuneBrand(ClientValue):
    contactITEmailAddress: str | None = None
    contactITName: str | None = None
    contactITNotes: str | None = None
    contactITPhoneNumber: str | None = None
    darkBackgroundLogo: MimeContent = field(default_factory=MimeContent)
    displayName: str | None = None
    lightBackgroundLogo: MimeContent = field(default_factory=MimeContent)
    onlineSupportSiteName: str | None = None
    onlineSupportSiteUrl: str | None = None
    privacyUrl: str | None = None
    showDisplayNameNextToLogo: bool | None = None
    showLogo: bool | None = None
    showNameNextToLogo: bool | None = None
    themeColor: RgbColor = field(default_factory=RgbColor)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IntuneBrand"
