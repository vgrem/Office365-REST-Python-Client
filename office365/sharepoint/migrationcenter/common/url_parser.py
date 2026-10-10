from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class MigrationUrlParser(Entity):
    """"""

    def __init__(
        self,
        context: ClientContext,
        user_input_destination_url: str,
        retrive_all_lists: bool,
        retrieve_all_lists_sub_folders: bool,
        force_my_site_default_list: bool,
        migration_type: str,
        current_context_site_subscription_id: str,
    ) -> None:
        static_path = ServiceOperationPath(
            "SP.AppContextSite",
            {
                "userInputDestinationUrl": user_input_destination_url,
                "retriveAllLists": retrive_all_lists,
                "retrieveAllListsSubFolders": retrieve_all_lists_sub_folders,
                "forceMySiteDefaultList": force_my_site_default_list,
                "migrationType": migration_type,
                "currentContextSiteSubscriptionId": current_context_site_subscription_id,
            },
        )
        super().__init__(context, static_path)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Common.MigrationUrlParser"

    @property
    def current_context_site_subscription_id(self) -> Optional[UUID]:
        """Gets the CurrentContextSiteSubscriptionId property"""
        return self.properties.get("CurrentContextSiteSubscriptionId", None)

    @property
    def force_my_site_default_list(self) -> Optional[bool]:
        """Gets the ForceMySiteDefaultList property"""
        return self.properties.get("ForceMySiteDefaultList", None)

    @property
    def max_folder_levels(self) -> Optional[int]:
        """Gets the MaxFolderLevels property"""
        return self.properties.get("MaxFolderLevels", None)

    @property
    def migration_type(self) -> Optional[str]:
        """Gets the MigrationType property"""
        return self.properties.get("MigrationType", None)

    @property
    def original_destination_url(self) -> Optional[str]:
        """Gets the OriginalDestinationUrl property"""
        return self.properties.get("OriginalDestinationUrl", None)

    @property
    def retrieve_all_lists(self) -> Optional[bool]:
        """Gets the RetrieveAllLists property"""
        return self.properties.get("RetrieveAllLists", None)

    @property
    def retrieve_sub_folders_for_all_lists(self) -> Optional[bool]:
        """Gets the RetrieveSubFoldersForAllLists property"""
        return self.properties.get("RetrieveSubFoldersForAllLists", None)
