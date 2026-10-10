from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.administration.sitemove.systemsitelockexpres import (
    SystemSiteLockExpirationResult,
)
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SiteMoveService(Entity):
    """ """

    def __init__(
        self,
        context: ClientContext,
        site_id: str,
        site_subscription_id: Optional[str] = None,
        source_database_id: Optional[str] = None,
        target_database_id: Optional[str] = None,
    ) -> None:
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
        super().__init__(context, static_path)

    def acquire_system_site_lock(
        self, lock_requestor: str, lock_type: int, lease_duration_in_minutes: int
    ) -> ClientResult[SystemSiteLockExpirationResult]:
        """"""
        return_type = ClientResult(self.context, SystemSiteLockExpirationResult())
        payload = {
            "lockRequestor": lock_requestor,
            "lockType": lock_type,
            "leaseDurationInMinutes": lease_duration_in_minutes,
        }
        qry = ServiceOperationQuery(self, "AcquireSystemSiteLock", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SiteMove.Service.SiteMoveService"

    def apply_replica_site_map_for_move(self) -> ClientResult[int]:
        """ApplyReplicaSiteMapForMove operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "ApplyReplicaSiteMapForMove", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_sp_site_content_database(self, site_id: str) -> ClientResult[bool]:
        """CheckSPSiteContentDatabase operation.

        Args:
            site_id (UUID): siteId parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CheckSPSiteContentDatabase", None, {"siteId": site_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def clear_site_relocation_marker(self) -> Self:
        """ClearSiteRelocationMarker operation."""
        qry = ServiceOperationQuery(self, "ClearSiteRelocationMarker", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def extend_system_site_lock_expiration(
        self, lease_duration_in_minute: int
    ) -> ClientResult[SystemSiteLockExpirationResult]:
        """ExtendSystemSiteLockExpiration operation.

        Args:
            lease_duration_in_minute (int): leaseDurationInMinute parameter
        """
        return_type = ClientResult(self.context, SystemSiteLockExpirationResult())
        qry = ServiceOperationQuery(
            self,
            "ExtendSystemSiteLockExpiration",
            None,
            {"leaseDurationInMinute": lease_duration_in_minute},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_all_docs_incremental_rows(self, serialized_document_ids: str) -> ClientResult[str]:
        """GetAllDocsIncrementalRows operation.

        Args:
            serialized_document_ids (str): serializedDocumentIds parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetAllDocsIncrementalRows",
            None,
            {"serializedDocumentIds": serialized_document_ids},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_all_docs_incremental_rows_stream(self, serialized_document_ids: str) -> ClientResult[bytes]:
        """GetAllDocsIncrementalRowsStream operation.

        Args:
            serialized_document_ids (str): serializedDocumentIds parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "GetAllDocsIncrementalRowsStream",
            None,
            {"serializedDocumentIds": serialized_document_ids},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_all_sites_deleted_and_bit_flags(self) -> ClientResult[str]:
        """GetAllSitesDeletedAndBitFlags operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetAllSitesDeletedAndBitFlags", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_app_principals_for_site_xml(self) -> ClientResult[str]:
        """GetAppPrincipalsForSiteXml operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetAppPrincipalsForSiteXml", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_blob_deletion_hold_until(self) -> ClientResult[str]:
        """GetBlobDeletionHoldUntil operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetBlobDeletionHoldUntil", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_cps_change_token(self) -> ClientResult[int]:
        """GetCPSChangeToken operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetCPSChangeToken", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_cps_site_delete_reason(self) -> ClientResult[int]:
        """GetCPSSiteDeleteReason operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetCPSSiteDeleteReason", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_crawl_queue_batch_count(self, include_crawl_url_join: bool) -> ClientResult[int]:
        """GetCrawlQueueBatchCount operation.

        Args:
            include_crawl_url_join (bool): includeCrawlUrlJoin parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "GetCrawlQueueBatchCount", None, {"includeCrawlUrlJoin": include_crawl_url_join}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_database_properties(self) -> ClientResult[str]:
        """GetDatabaseProperties operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetDatabaseProperties", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_chunk(self, table_name: str, schema_name: str) -> ClientResult[str]:
        """GetDataChunk operation.

        Args:
            table_name (str): tableName parameter
            schema_name (str): schemaName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetDataChunk", None, {"tableName": table_name, "schemaName": schema_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_data_chunks(self) -> ClientResult[str]:
        """GetDataChunks operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetDataChunks", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_chunks_iterator(self) -> ClientResult[str]:
        """GetDataChunksIterator operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetDataChunksIterator", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_chunks_iterator_stream(self) -> ClientResult[bytes]:
        """GetDataChunksIteratorStream operation."""
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "GetDataChunksIteratorStream", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_reader(self, sql_command_text: str) -> ClientResult[str]:
        """GetDataReader operation.

        Args:
            sql_command_text (str): sqlCommandText parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetDataReader", None, {"sqlCommandText": sql_command_text}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_data_reader_stream(self, sql_command_text: str) -> ClientResult[bytes]:
        """GetDataReaderStream operation.

        Args:
            sql_command_text (str): sqlCommandText parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetDataReaderStream", None, {"sqlCommandText": sql_command_text}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_db_activities(self) -> ClientResult[str]:
        """GetDBActivities operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetDBActivities", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_event_cache_checksum_stats_json(self, lower_bound: int, upper_bound: int) -> ClientResult[str]:
        """GetEventCacheChecksumStatsJson operation.

        Args:
            lower_bound (int): lowerBound parameter
            upper_bound (int): upperBound parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetEventCacheChecksumStatsJson",
            None,
            {"lowerBound": lower_bound, "upperBound": upper_bound},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_data_chunk(self, last_copied_id: int, search_change_token: int) -> ClientResult[str]:
        """GetEventCacheDataChunk operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
            search_change_token (int): searchChangeToken parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetEventCacheDataChunk",
            None,
            {"lastCopiedId": last_copied_id, "searchChangeToken": search_change_token},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_data_chunk_iterator(self, last_copied_id: int, search_change_token: int) -> ClientResult[str]:
        """GetEventCacheDataChunkIterator operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
            search_change_token (int): searchChangeToken parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetEventCacheDataChunkIterator",
            None,
            {"lastCopiedId": last_copied_id, "searchChangeToken": search_change_token},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_data_chunk_iterator_stream(
        self, last_copied_id: int, search_change_token: int
    ) -> ClientResult[bytes]:
        """GetEventCacheDataChunkIteratorStream operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
            search_change_token (int): searchChangeToken parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "GetEventCacheDataChunkIteratorStream",
            None,
            {"lastCopiedId": last_copied_id, "searchChangeToken": search_change_token},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ex_checksum_stats_json(self, lower_bound: int, upper_bound: int) -> ClientResult[str]:
        """GetEventCacheExChecksumStatsJson operation.

        Args:
            lower_bound (int): lowerBound parameter
            upper_bound (int): upperBound parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetEventCacheExChecksumStatsJson",
            None,
            {"lowerBound": lower_bound, "upperBound": upper_bound},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ex_columns(self) -> ClientResult[str]:
        """GetEventCacheExColumns operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetEventCacheExColumns", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ex_data_chunk(self, last_copied_id: int) -> ClientResult[str]:
        """GetEventCacheExDataChunk operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetEventCacheExDataChunk", None, {"lastCopiedId": last_copied_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ex_data_chunk_iterator(self, last_copied_id: int) -> ClientResult[str]:
        """GetEventCacheExDataChunkIterator operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetEventCacheExDataChunkIterator", None, {"lastCopiedId": last_copied_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ex_data_chunk_iterator_stream(self, last_copied_id: int) -> ClientResult[bytes]:
        """GetEventCacheExDataChunkIteratorStream operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetEventCacheExDataChunkIteratorStream", None, {"lastCopiedId": last_copied_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ids(self, last_copied_id: int) -> ClientResult[str]:
        """GetEventCacheIds operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetEventCacheIds", None, {"lastCopiedId": last_copied_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_event_cache_ids_stream(self, last_copied_id: int) -> ClientResult[bytes]:
        """GetEventCacheIdsStream operation.

        Args:
            last_copied_id (int): lastCopiedId parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetEventCacheIdsStream", None, {"lastCopiedId": last_copied_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_extension_schema_row_counts_json(self) -> ClientResult[str]:
        """GetExtensionSchemaRowCountsJson operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetExtensionSchemaRowCountsJson", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_farm_properties(self) -> ClientResult[str]:
        """GetFarmProperties operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetFarmProperties", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_marker(self) -> ClientResult[str]:
        """GetMarker operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetMarker", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_per_column_checksums(self, schema_name: str, table_name: str) -> ClientResult[str]:
        """GetPerColumnChecksums operation.

        Args:
            schema_name (str): schemaName parameter
            table_name (str): tableName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetPerColumnChecksums", None, {"schemaName": schema_name, "tableName": table_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_post_lock_event_summary_json(self, watermark: int) -> ClientResult[str]:
        """GetPostLockEventSummaryJson operation.

        Args:
            watermark (int): watermark parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetPostLockEventSummaryJson", None, {"watermark": watermark}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_random_access_data_chunk(self, table_name: str, schema_name: str) -> ClientResult[str]:
        """GetRandomAccessDataChunk operation.

        Args:
            table_name (str): tableName parameter
            schema_name (str): schemaName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetRandomAccessDataChunk",
            None,
            {"tableName": table_name, "schemaName": schema_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_replica_farm_targets(self) -> ClientResult[str]:
        """GetReplicaFarmTargets operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetReplicaFarmTargets", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_scalar_value(self, sql_command_text: str) -> ClientResult[int]:
        """GetScalarValue operation.

        Args:
            sql_command_text (str): sqlCommandText parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "GetScalarValue", None, {"sqlCommandText": sql_command_text}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_scp_events_in_processing_count(self) -> ClientResult[int]:
        """GetScpEventsInProcessingCount operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetScpEventsInProcessingCount", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_service_version(self) -> ClientResult[int]:
        """GetServiceVersion operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetServiceVersion", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_deletion_restorable_and_migration_flags(self) -> ClientResult[str]:
        """GetSiteDeletionRestorableAndMigrationFlags operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteDeletionRestorableAndMigrationFlags", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_deletion_time(self) -> ClientResult[str]:
        """GetSiteDeletionTime operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteDeletionTime", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_ip_label_tooltip_xml(self) -> ClientResult[str]:
        """GetSiteIpLabelTooltipXml operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteIpLabelTooltipXml", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_move_state(self) -> ClientResult[str]:
        """GetSiteMoveState operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteMoveState", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_properties(self) -> ClientResult[str]:
        """GetSiteProperties operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteProperties", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_relocation_compatible_schema_version(self) -> ClientResult[str]:
        """GetSiteRelocationCompatibleSchemaVersion operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteRelocationCompatibleSchemaVersion", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sp_deleted_site_relocation_status(self, check_lock_time: bool) -> ClientResult[str]:
        """GetSPDeletedSiteRelocationStatus operation.

        Args:
            check_lock_time (bool): checkLockTime parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetSPDeletedSiteRelocationStatus", None, {"checkLockTime": check_lock_time}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_table_data_chunk(self, table_name: str, schema_name: str) -> ClientResult[str]:
        """GetTableDataChunk operation.

        Args:
            table_name (str): tableName parameter
            schema_name (str): schemaName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetTableDataChunk", None, {"tableName": table_name, "schemaName": schema_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_table_data_chunk_iterator(self, table_name: str, schema_name: str) -> ClientResult[str]:
        """GetTableDataChunkIterator operation.

        Args:
            table_name (str): tableName parameter
            schema_name (str): schemaName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetTableDataChunkIterator",
            None,
            {"tableName": table_name, "schemaName": schema_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_table_data_chunk_iterator_stream(self, table_name: str, schema_name: str) -> ClientResult[bytes]:
        """GetTableDataChunkIteratorStream operation.

        Args:
            table_name (str): tableName parameter
            schema_name (str): schemaName parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "GetTableDataChunkIteratorStream",
            None,
            {"tableName": table_name, "schemaName": schema_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_table_row_count(self, schema_name: str, table_name: str) -> ClientResult[int]:
        """GetTableRowCount operation.

        Args:
            schema_name (str): schemaName parameter
            table_name (str): tableName parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "GetTableRowCount", None, {"schemaName": schema_name, "tableName": table_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_tenant_workflows(self) -> ClientResult[StringCollection]:
        """GetTenantWorkflows operation."""
        return_type = ClientResult(self.context, StringCollection())
        qry = ServiceOperationQuery(self, "GetTenantWorkflows", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_validation_chunks(self) -> ClientResult[str]:
        """GetValidationChunks operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetValidationChunks", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_work_item(self) -> ClientResult[str]:
        """GetWorkItem operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetWorkItem", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def has_event_cache_duplicate_time(self, target_ident_current: int, source_count: int) -> ClientResult[bool]:
        """HasEventCacheDuplicateTime operation.

        Args:
            target_ident_current (int): targetIdentCurrent parameter
            source_count (int): sourceCount parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "HasEventCacheDuplicateTime",
            None,
            {"targetIdentCurrent": target_ident_current, "sourceCount": source_count},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def hold_blob_deletion_on_source(self, hold_days: int) -> Self:
        """HoldBlobDeletionOnSource operation.

        Args:
            hold_days (int): holdDays parameter
        """
        qry = ServiceOperationQuery(self, "HoldBlobDeletionOnSource", None, {"holdDays": hold_days}, None, None)
        self.context.add_query(qry)
        return self

    def is_db_read_only(self) -> ClientResult[bool]:
        """IsDbReadOnly operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsDbReadOnly", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_system_site_locked(self, lock_requester: str) -> ClientResult[bool]:
        """IsSystemSiteLocked operation.

        Args:
            lock_requester (str): lockRequester parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "IsSystemSiteLocked", None, {"lockRequester": lock_requester}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def lock_site(self) -> ClientResult[int]:
        """LockSite operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "LockSite", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def pause_crawling(self, original_cps_delete_reason: int) -> Self:
        """PauseCrawling operation.

        Args:
            original_cps_delete_reason (Int16): originalCPSDeleteReason parameter
        """
        qry = ServiceOperationQuery(
            self, "PauseCrawling", None, {"originalCPSDeleteReason": original_cps_delete_reason}, None, None
        )
        self.context.add_query(qry)
        return self

    def process_storage_metrics_changes(self) -> Self:
        """ProcessStorageMetricsChanges operation."""
        qry = ServiceOperationQuery(self, "ProcessStorageMetricsChanges", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def pulse_heartbeat(self) -> Self:
        """PulseHeartbeat operation."""
        qry = ServiceOperationQuery(self, "PulseHeartbeat", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def release_system_site_lock(self, lock_requester: str) -> ClientResult[int]:
        """ReleaseSystemSiteLock operation.

        Args:
            lock_requester (str): lockRequester parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "ReleaseSystemSiteLock", None, {"lockRequester": lock_requester}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def remove_site_map_entry(self) -> Self:
        """RemoveSiteMapEntry operation."""
        qry = ServiceOperationQuery(self, "RemoveSiteMapEntry", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def remove_site_map_entry_clear_cache(self, site_path: str) -> Self:
        """RemoveSiteMapEntry_ClearCache operation.

        Args:
            site_path (str): sitePath parameter
        """
        qry = ServiceOperationQuery(self, "RemoveSiteMapEntry_ClearCache", None, {"sitePath": site_path}, None, None)
        self.context.add_query(qry)
        return self

    def resume_crawling(self, original_cps_delete_reason: int) -> Self:
        """ResumeCrawling operation.

        Args:
            original_cps_delete_reason (Int16): originalCPSDeleteReason parameter
        """
        qry = ServiceOperationQuery(
            self, "ResumeCrawling", None, {"originalCPSDeleteReason": original_cps_delete_reason}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_site_move_state(self, state: int) -> Self:
        """SetSiteMoveState operation.

        Args:
            state (int): state parameter
        """
        qry = ServiceOperationQuery(self, "SetSiteMoveState", None, {"state": state}, None, None)
        self.context.add_query(qry)
        return self

    def source_cleanup_after_move(self, is_deleted: bool) -> Self:
        """SourceCleanupAfterMove operation.

        Args:
            is_deleted (bool): isDeleted parameter
        """
        qry = ServiceOperationQuery(self, "SourceCleanupAfterMove", None, {"isDeleted": is_deleted}, None, None)
        self.context.add_query(qry)
        return self

    def start_snapshot_isolation(self) -> Self:
        """StartSnapshotIsolation operation."""
        qry = ServiceOperationQuery(self, "StartSnapshotIsolation", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def stop_session_token(self) -> Self:
        """StopSessionToken operation."""
        qry = ServiceOperationQuery(self, "StopSessionToken", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def unlock_site_on_failure(self, original_lock_flags: int) -> Self:
        """UnlockSiteOnFailure operation.

        Args:
            original_lock_flags (int): originalLockFlags parameter
        """
        qry = ServiceOperationQuery(
            self, "UnlockSiteOnFailure", None, {"originalLockFlags": original_lock_flags}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_abs_blob_dates(self) -> Self:
        """UpdateAbsBlobDates operation."""
        qry = ServiceOperationQuery(self, "UpdateAbsBlobDates", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def verify_replica_site_map_for_move(self) -> ClientResult[int]:
        """VerifyReplicaSiteMapForMove operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "VerifyReplicaSiteMapForMove", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_telemetry_only_work_item(self) -> ClientResult[bool]:
        """DeleteTelemetryOnlyWorkItem operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "DeleteTelemetryOnlyWorkItem", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_perms_incremental_rows(self, serialized_scope_ids: str) -> ClientResult[str]:
        """GetPermsIncrementalRows operation.

        Args:
            serialized_scope_ids (str):
                serializedScopeIds parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetPermsIncrementalRows", None, {"serializedScopeIds": serialized_scope_ids}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_perms_incremental_rows_stream(self, serialized_scope_ids: str) -> ClientResult[bytes]:
        """GetPermsIncrementalRowsStream operation.

        Args:
            serialized_scope_ids (str):
                serializedScopeIds parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetPermsIncrementalRowsStream", None, {"serializedScopeIds": serialized_scope_ids}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_site_changes(
        self, from_change_number: int, to_change_number: int, has_to_change_number: bool, max_changes: int
    ) -> ClientResult[str]:
        """GetSiteChanges operation.

        Args:
            from_change_number (int):
                fromChangeNumber parameter
            to_change_number (int):
                toChangeNumber parameter
            has_to_change_number (bool):
                hasToChangeNumber parameter
            max_changes (int):
                maxChanges parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetSiteChanges",
            None,
            {
                "fromChangeNumber": from_change_number,
                "toChangeNumber": to_change_number,
                "hasToChangeNumber": has_to_change_number,
                "maxChanges": max_changes,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
