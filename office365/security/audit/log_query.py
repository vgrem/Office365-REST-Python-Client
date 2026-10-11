from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.audit.logs.recordtype import AuditLogRecordType
    from office365.security.audit.audit_log_query_status import (
        AuditLogQueryStatus,
    )
    from office365.security.audit.log_record import AuditLogRecord


class AuditLogQuery(Entity):
    @property
    def administrative_unit_id_filters(self) -> StringCollection:
        """Gets the administrativeUnitIdFilters property"""
        return self.properties.get("administrativeUnitIdFilters", StringCollection())

    @property
    def approximate_returned_record_count(self) -> Optional[int]:
        """Gets the approximateReturnedRecordCount property"""
        return self.properties.get("approximateReturnedRecordCount", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def filter_end_date_time(self) -> Optional[datetime]:
        """Gets the filterEndDateTime property"""
        return self.properties.get("filterEndDateTime", datetime.min)

    @property
    def filter_start_date_time(self) -> Optional[datetime]:
        """Gets the filterStartDateTime property"""
        return self.properties.get("filterStartDateTime", datetime.min)

    @property
    def ip_address_filters(self) -> StringCollection:
        """Gets the ipAddressFilters property"""
        return self.properties.get("ipAddressFilters", StringCollection())

    @property
    def is_record_count_limit_exceeded(self) -> Optional[bool]:
        """Gets the isRecordCountLimitExceeded property"""
        return self.properties.get("isRecordCountLimitExceeded", None)

    @property
    def keyword_filter(self) -> Optional[str]:
        """Gets the keywordFilter property"""
        return self.properties.get("keywordFilter", None)

    @property
    def object_id_filters(self) -> StringCollection:
        """Gets the objectIdFilters property"""
        return self.properties.get("objectIdFilters", StringCollection())

    @property
    def operation_filters(self) -> StringCollection:
        """Gets the operationFilters property"""
        return self.properties.get("operationFilters", StringCollection())

    @property
    def record_count_limit(self) -> Optional[int]:
        """Gets the recordCountLimit property"""
        return self.properties.get("recordCountLimit", None)

    @property
    def record_type_filters(self) -> ClientValueCollection[AuditLogRecordType]:
        """Gets the recordTypeFilters property"""
        from office365.directory.audit.logs.recordtype import AuditLogRecordType

        return self.properties.get("recordTypeFilters", ClientValueCollection[AuditLogRecordType](AuditLogRecordType))

    @property
    def service_filters(self) -> StringCollection:
        """Gets the serviceFilters property"""
        return self.properties.get("serviceFilters", StringCollection())

    @property
    def status(self) -> AuditLogQueryStatus:
        """Gets the status property"""
        from office365.security.audit.audit_log_query_status import (
            AuditLogQueryStatus,
        )

        return self.properties.get("status", AuditLogQueryStatus.notStarted)

    @property
    def user_principal_name_filters(self) -> StringCollection:
        """Gets the userPrincipalNameFilters property"""
        return self.properties.get("userPrincipalNameFilters", StringCollection())

    @property
    def records(self) -> EntityCollection[AuditLogRecord]:
        """Gets the records property"""
        from office365.security.audit.log_record import AuditLogRecord

        return self.properties.get(
            "records",
            EntityCollection[AuditLogRecord](self.context, AuditLogRecord, ResourcePath("records", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AuditLogQuery"
