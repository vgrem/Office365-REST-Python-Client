from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.partners.billing.blob import Blob


class Manifest(Entity):
    @property
    def blob_count(self) -> Optional[int]:
        """Gets the blobCount property"""
        return self.properties.get("blobCount", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def data_format(self) -> Optional[str]:
        """Gets the dataFormat property"""
        return self.properties.get("dataFormat", None)

    @property
    def e_tag(self) -> Optional[str]:
        """Gets the eTag property"""
        return self.properties.get("eTag", None)

    @property
    def partition_type(self) -> Optional[str]:
        """Gets the partitionType property"""
        return self.properties.get("partitionType", None)

    @property
    def partner_tenant_id(self) -> Optional[str]:
        """Gets the partnerTenantId property"""
        return self.properties.get("partnerTenantId", None)

    @property
    def root_directory(self) -> Optional[str]:
        """Gets the rootDirectory property"""
        return self.properties.get("rootDirectory", None)

    @property
    def sas_token(self) -> Optional[str]:
        """Gets the sasToken property"""
        return self.properties.get("sasToken", None)

    @property
    def schema_version(self) -> Optional[str]:
        """Gets the schemaVersion property"""
        return self.properties.get("schemaVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.Manifest"

    @property
    def blobs(self) -> ClientValueCollection[Blob]:
        """Gets the blobs property"""
        from office365.partners.billing.blob import Blob

        return self.properties.get("blobs", ClientValueCollection[Blob](Blob))
