from __future__ import annotations

from office365.directory.identitygovernance.termsofuse.agreement_file_properties import (
    AgreementFileProperties,
)
from office365.directory.identitygovernance.termsofuse.agreement_file_version import AgreementFileVersion
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class AgreementFileLocalization(AgreementFileProperties):
    @property
    def versions(self) -> EntityCollection[AgreementFileVersion]:
        """Gets the versions property"""
        return self.properties.get(
            "versions",
            EntityCollection[AgreementFileVersion](
                self.context, AgreementFileVersion, ResourcePath("versions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AgreementFileLocalization"
