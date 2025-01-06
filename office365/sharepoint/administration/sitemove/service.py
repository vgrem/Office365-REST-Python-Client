from typing import TYPE_CHECKING

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SiteMoveService(Entity):
    """ """

    def __init__(
        self,
        context,
        site_id,
        site_subscription_id=None,
        source_database_id=None,
        target_database_id=None,
    ):
        # type: (ClientContext, str, str, str, str) -> None
        """"""
        static_path = ServiceOperationPath(
            "Microsoft.SharePoint.Administration.SiteMove.Service.SiteMoveService",
            {
                "siteId": site_id,
                "siteSubscriptionId": site_subscription_id,
                "sourceDatabaseId": source_database_id,
                "targetDatabaseId": target_database_id,
            },
        )
        super(SiteMoveService, self).__init__(context, static_path)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SiteMove.Service.SiteMoveService"
