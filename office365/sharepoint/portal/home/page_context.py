from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class SharePointHomePageContext(ClientValue):
    ActiveFlights: Optional[StringCollection] = None
    AlternateWebAppHost: Optional[str] = None
    ExperienceState: Optional[int] = None
    IsGraphEnabled: Optional[bool] = None
    IsGroupCreationNewUXEnabled: Optional[bool] = None
    IsLoggingUploadEnabled: Optional[bool] = None
    IsMobile: Optional[bool] = None
    IsModernSearchEnabled: Optional[bool] = None
    IsOrgLinksProvisioned: Optional[bool] = None
    IsRtl: Optional[bool] = None
    IsSelfServiceSiteCreationEnabled: Optional[bool] = None
    IsUserVoiceEnabled: Optional[bool] = None
    LoadSuiteNav: Optional[bool] = None
    MicroserviceFlights: StringCollection = field(default_factory=StringCollection)
    MicroserviceUrl: Optional[str] = None
    MySiteUrl: Optional[str] = None
    SearchCenterUrl: Optional[str] = None
    ShowCreateNewsTeachingBubble: Optional[bool] = None
    ShowFirstRunExperience: Optional[bool] = None
    ShowMobileUpsell: Optional[bool] = None
    UserAcronym: Optional[str] = None
    UserBannerColor: Optional[str] = None
    UserPhotoCdnBaseUrl: Optional[str] = None
    VideoChannelUrlTemplate: Optional[str] = None
    VideoPlayerUrlTemplate: Optional[str] = None

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.Home.SharePointHomePageContext"

    CustomFormURL: str | None = None

    IsSmartWikiEntryEnabled: bool | None = None
