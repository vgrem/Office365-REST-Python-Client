from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.internal.canonymouslinkuselimit import (
    CAnonymousLinkUseLimit,
)

if TYPE_CHECKING:
    from office365.sharepoint.sharing.cexternalsharingthrottling import (
        CExternalSharingThrottling,
    )
    from office365.sharepoint.sharing.internal.cexternalsharingenforcement import (
        CExternalSharingEnforcement,
    )


class SharingRestrictions(Entity):
    """ """

    def __init__(self, context):
        static_path = ResourcePath("Microsoft.SharePoint.Sharing.Internal.SharingRestrictions")
        super().__init__(context, static_path)

    @property
    def anonymous_link_use_limit(self):
        return self.properties.get("anonymousLinkUseLimit", CAnonymousLinkUseLimit())

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Sharing.Internal.SharingRestrictions"

    @property
    def external_sharing_enforcement(self) -> CExternalSharingEnforcement:
        """Gets the externalSharingEnforcement property"""
        from office365.sharepoint.sharing.internal.cexternalsharingenforcement import (
            CExternalSharingEnforcement,
        )

        return self.properties.get("externalSharingEnforcement", CExternalSharingEnforcement())

    @property
    def external_sharing_throttling(self) -> CExternalSharingThrottling:
        """Gets the externalSharingThrottling property"""
        from office365.sharepoint.sharing.cexternalsharingthrottling import (
            CExternalSharingThrottling,
        )

        return self.properties.get("externalSharingThrottling", CExternalSharingThrottling())
