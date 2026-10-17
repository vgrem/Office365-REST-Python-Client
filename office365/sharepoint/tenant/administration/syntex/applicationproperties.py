from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.sharepoint.tenant.administration.spofileversionfiletypepolicysettings import (
    SPOFileVersionFileTypePolicySettings,
)


@dataclass
class SPSyntexApplicationProperties(ClientValue):
    ApplicationId: UUID | None = None
    ApplicationName: str | None = None
    Applications: GuidCollection = field(default_factory=GuidCollection)
    AppOnlyPermissions: StringCollection = field(default_factory=StringCollection)
    CopilotEmbeddedChatHosts: StringCollection = field(default_factory=StringCollection)
    DelegatedPermissions: StringCollection = field(default_factory=StringCollection)
    OverrideTenantSharingCapability: bool | None = None
    OverrideTenantSharingCapabilityNullable: int | None = None
    OwningApplicationId: UUID | None = None
    OwningApplicationName: str | None = None
    SharingCapability: int | None = None
    ItemMajorVersionLimit: int | None = None

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPSyntexApplicationProperties"

    EnableAutoExpirationVersionTrim: int | None = None

    ExpireVersionsAfterDays: int | None = None

    FileTypesForVersionExpiration: StringCollection = field(default_factory=StringCollection)

    RemoveVersionExpirationFileTypeOverride: StringCollection = field(default_factory=StringCollection)

    VersionPolicyFileTypeOverride: ClientValueCollection[SPOFileVersionFileTypePolicySettings] = field(
        default_factory=lambda: ClientValueCollection(SPOFileVersionFileTypePolicySettings)
    )
