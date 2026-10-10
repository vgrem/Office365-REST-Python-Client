from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity


class SPMachineLearningSample(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningSample"

    @property
    def created(self) -> Optional[datetime]:
        """Gets the Created property"""
        return self.properties.get("Created", datetime.min)

    @property
    def created_by(self) -> Optional[str]:
        """Gets the CreatedBy property"""
        return self.properties.get("CreatedBy", None)

    @property
    def created_by_name(self) -> Optional[str]:
        """Gets the CreatedByName property"""
        return self.properties.get("CreatedByName", None)

    @property
    def drive_id(self) -> Optional[str]:
        """Gets the DriveId property"""
        return self.properties.get("DriveId", None)

    @property
    def etag(self) -> Optional[str]:
        """Gets the Etag property"""
        return self.properties.get("Etag", None)

    @property
    def extracted_text(self) -> Optional[str]:
        """Gets the ExtractedText property"""
        return self.properties.get("ExtractedText", None)

    @property
    def file_leaf_ref(self) -> Optional[str]:
        """Gets the FileLeafRef property"""
        return self.properties.get("FileLeafRef", None)

    @property
    def file_ref(self) -> Optional[str]:
        """Gets the FileRef property"""
        return self.properties.get("FileRef", None)

    @property
    def file_type(self) -> Optional[str]:
        """Gets the FileType property"""
        return self.properties.get("FileType", None)

    @property
    def fs_obj_type(self) -> Optional[int]:
        """Gets the FSObjType property"""
        return self.properties.get("FSObjType", None)

    @property
    def id_(self) -> Optional[int]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListID property"""
        return self.properties.get("ListID", None)

    @property
    def markups(self) -> Optional[str]:
        """Gets the Markups property"""
        return self.properties.get("Markups", None)

    @property
    def model_ids(self) -> ClientValueCollection:
        """Gets the ModelIds property"""
        return self.properties.get("ModelIds", ClientValueCollection(int))

    @property
    def modified(self) -> Optional[datetime]:
        """Gets the Modified property"""
        return self.properties.get("Modified", datetime.min)

    @property
    def modified_by(self) -> Optional[str]:
        """Gets the ModifiedBy property"""
        return self.properties.get("ModifiedBy", None)

    @property
    def modified_by_name(self) -> Optional[str]:
        """Gets the ModifiedByName property"""
        return self.properties.get("ModifiedByName", None)

    @property
    def object_id(self) -> Optional[str]:
        """Gets the ObjectId property"""
        return self.properties.get("ObjectId", None)

    @property
    def server_redirected_embed_uri(self) -> Optional[str]:
        """Gets the ServerRedirectedEmbedUri property"""
        return self.properties.get("ServerRedirectedEmbedUri", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def token_end_position(self) -> ClientValueCollection:
        """Gets the TokenEndPosition property"""
        return self.properties.get("TokenEndPosition", ClientValueCollection(int))

    @property
    def token_start_position(self) -> ClientValueCollection:
        """Gets the TokenStartPosition property"""
        return self.properties.get("TokenStartPosition", ClientValueCollection(int))

    @property
    def unique_id(self) -> Optional[UUID]:
        """Gets the UniqueId property"""
        return self.properties.get("UniqueId", None)

    @property
    def id(self) -> Optional[int]:
        """Gets the ID property"""
        return self.properties.get("ID", None)
