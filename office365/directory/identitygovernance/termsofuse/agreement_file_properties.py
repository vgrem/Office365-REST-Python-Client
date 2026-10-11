from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identitygovernance.termsofuse.agreement_file_data import (
        AgreementFileData,
    )


class AgreementFileProperties(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def file_name(self) -> Optional[str]:
        """Gets the fileName property"""
        return self.properties.get("fileName", None)

    @property
    def is_default(self) -> Optional[bool]:
        """Gets the isDefault property"""
        return self.properties.get("isDefault", None)

    @property
    def is_major_version(self) -> Optional[bool]:
        """Gets the isMajorVersion property"""
        return self.properties.get("isMajorVersion", None)

    @property
    def language(self) -> Optional[str]:
        """Gets the language property"""
        return self.properties.get("language", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AgreementFileProperties"

    @property
    def file_data(self) -> AgreementFileData:
        """Gets the fileData property"""
        from office365.directory.identitygovernance.termsofuse.agreement_file_data import (
            AgreementFileData,
        )

        return self.properties.get("fileData", AgreementFileData())
