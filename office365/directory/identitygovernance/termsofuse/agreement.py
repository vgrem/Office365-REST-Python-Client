from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.termsofuse.agreement_acceptance import (
    AgreementAcceptance,
)
from office365.directory.identitygovernance.termsofuse.agreement_file import (
    AgreementFile,
)
from office365.directory.identitygovernance.termsofuse.agreement_file_localization import (
    AgreementFileLocalization,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.termsofuse.terms_expiration import (
        TermsExpiration,
    )


class Agreement(Entity):
    """
    Represents a tenant's customizable terms of use agreement that is created and managed with
    Azure Active Directory (Azure AD). You can use the following methods to create and manage the Azure Active Directory
    Terms of Use feature according to your scenario.
    """

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_per_device_acceptance_required(self) -> Optional[bool]:
        """Gets the isPerDeviceAcceptanceRequired property"""
        return self.properties.get("isPerDeviceAcceptanceRequired", None)

    @property
    def is_viewing_before_acceptance_required(self) -> Optional[bool]:
        """Gets the isViewingBeforeAcceptanceRequired property"""
        return self.properties.get("isViewingBeforeAcceptanceRequired", None)

    @property
    def user_reaccept_required_frequency(self) -> timedelta:
        """Gets the userReacceptRequiredFrequency property"""
        return self.properties.get("userReacceptRequiredFrequency", timedelta.min)

    @property
    def acceptances(self) -> EntityCollection[AgreementAcceptance]:
        """Gets the acceptances property"""
        return self.properties.get(
            "acceptances",
            EntityCollection[AgreementAcceptance](
                self.context, AgreementAcceptance, ResourcePath("acceptances", self.resource_path)
            ),
        )

    @property
    def file(self) -> AgreementFile:
        """Gets the file property"""
        return self.properties.get("file", AgreementFile(self.context, ResourcePath("file", self.resource_path)))

    @property
    def files(self) -> EntityCollection[AgreementFileLocalization]:
        """Gets the files property"""
        return self.properties.get(
            "files",
            EntityCollection[AgreementFileLocalization](
                self.context, AgreementFileLocalization, ResourcePath("files", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Agreement"

    @property
    def terms_expiration(self) -> TermsExpiration:
        """Gets the termsExpiration property"""
        from office365.directory.identitygovernance.termsofuse.terms_expiration import (
            TermsExpiration,
        )

        return self.properties.get("termsExpiration", TermsExpiration())
