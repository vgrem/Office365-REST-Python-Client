from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.lists.batch_convert_result import BatchConvertResult

if TYPE_CHECKING:
    from office365.sharepoint.lists.batch_convert_classic_wiki_page_input import (
        BatchConvertClassicWikiPageInput,
    )
    from office365.sharepoint.lists.smart_wiki_metadata_update_parameters import (
        SmartWikiMetadataUpdateParameters,
    )


class SmartWikiLibraryUtility(Entity):
    def batch_convert_classic_wiki_pages(
        self,
        source_list_id: str,
        source_item_ids: list[str],
        target_web_url: str,
        target_list_id: str,
        use_fast_unordered_mode: bool,
        parent_unique_id: str,
        strict_asset_copy: bool,
    ) -> ClientResult[BatchConvertResult]:
        """BatchConvertClassicWikiPages operation.

        Args:
            source_list_id (str): sourceListId parameter
            source_item_ids (list[str]): sourceItemIds parameter
            target_web_url (str): targetWebUrl parameter
            target_list_id (str): targetListId parameter
            use_fast_unordered_mode (bool): useFastUnorderedMode parameter
            parent_unique_id (str): parentUniqueId parameter
            strict_asset_copy (bool): strictAssetCopy parameter
        """
        return_type = ClientResult(self.context, BatchConvertResult())
        qry = ServiceOperationQuery(
            self,
            "BatchConvertClassicWikiPages",
            None,
            {
                "sourceListId": source_list_id,
                "sourceItemIds": StringCollection(source_item_ids),
                "targetWebUrl": target_web_url,
                "targetListId": target_list_id,
                "useFastUnorderedMode": use_fast_unordered_mode,
                "parentUniqueId": parent_unique_id,
                "strictAssetCopy": strict_asset_copy,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def ensure_smart_wiki_library_feature(self) -> Self:
        """EnsureSmartWikiLibraryFeature operation."""
        qry = ServiceOperationQuery(self, "EnsureSmartWikiLibraryFeature", None, {}, None, None)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.SmartWikiLibrary.SmartWikiLibraryUtility"

    def get_skill_status(self, list_id: str) -> ClientResult[str]:
        """GetSkillStatus operation.

        Args:
            list_id (str):
                listId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetSkillStatus", [list_id], return_type)
        self.context.add_query(qry)
        return return_type

    def set_skill_status(self, list_id: str, skill_status: str) -> Self:
        """SetSkillStatus operation.

        Args:
            list_id (str):
                listId parameter
            skill_status (str):
                skillStatus parameter
        """
        qry = ServiceOperationQuery(
            self, "SetSkillStatus", None, {"listId": list_id, "skillStatus": skill_status}, None, None
        )
        self.context.add_query(qry)
        return self

    def batch_convert_classic_wiki_pages_v2(
        self,
        source_list_id: str,
        pages: ClientValueCollection[BatchConvertClassicWikiPageInput],
        target_web_url: str,
        target_list_id: str,
        parent_unique_id: str,
    ) -> ClientResult[BatchConvertResult]:
        """BatchConvertClassicWikiPagesV2 operation.

        Args:
            source_list_id (str):
                sourceListId parameter
            pages (ClientValueCollection[BatchConvertClassicWikiPageInput]):
                pages parameter
            target_web_url (str):
                targetWebUrl parameter
            target_list_id (str):
                targetListId parameter
            parent_unique_id (str):
                parentUniqueId parameter
        """
        from office365.sharepoint.lists.batch_convert_result import BatchConvertResult

        return_type = ClientResult(self.context, BatchConvertResult())
        qry = ServiceOperationQuery(
            self,
            "BatchConvertClassicWikiPagesV2",
            None,
            {
                "sourceListId": source_list_id,
                "pages": pages,
                "targetWebUrl": target_web_url,
                "targetListId": target_list_id,
                "parentUniqueId": parent_unique_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_file_metadata(self, list_id: str, item_id: str, metadata: SmartWikiMetadataUpdateParameters) -> Self:
        """SetFileMetadata operation.

        Args:
            list_id (str):
                listId parameter
            item_id (str):
                itemId parameter
            metadata (SmartWikiMetadataUpdateParameters):
                metadata parameter
        """
        qry = ServiceOperationQuery(
            self, "SetFileMetadata", None, {"listId": list_id, "itemId": item_id, "metadata": metadata}, None, None
        )
        self.context.add_query(qry)
        return self
