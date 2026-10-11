from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.audit.logs.recordtype import AuditLogRecordType
    from office365.directory.audit.logs.usertype import AuditLogUserType
    from office365.security.audit.audit_data import AuditData


class AuditLogRecord(Entity):
    @property
    def administrative_units(self) -> StringCollection:
        """Gets the administrativeUnits property"""
        return self.properties.get("administrativeUnits", StringCollection())

    @property
    def audit_data(self) -> AuditData:
        """Gets the auditData property"""
        from office365.security.audit.audit_data import AuditData

        return self.properties.get("auditData", AuditData())

    @property
    def audit_log_record_type(self) -> AuditLogRecordType:
        """Gets the auditLogRecordType property"""
        from office365.directory.audit.logs.recordtype import AuditLogRecordType

        return self.properties.get("auditLogRecordType", AuditLogRecordType.ExchangeAdmin)

    @property
    def client_ip(self) -> Optional[str]:
        """Gets the clientIp property"""
        return self.properties.get("clientIp", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def object_id(self) -> Optional[str]:
        """Gets the objectId property"""
        return self.properties.get("objectId", None)

    @property
    def operation(self) -> Optional[str]:
        """Gets the operation property"""
        return self.properties.get("operation", None)

    @property
    def organization_id(self) -> Optional[str]:
        """Gets the organizationId property"""
        return self.properties.get("organizationId", None)

    @property
    def service(self) -> Optional[str]:
        """Gets the service property"""
        return self.properties.get("service", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def user_type(self) -> AuditLogUserType:
        """Gets the userType property"""
        from office365.directory.audit.logs.usertype import AuditLogUserType

        return self.properties.get("userType", AuditLogUserType.Regular)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AuditLogRecord"
