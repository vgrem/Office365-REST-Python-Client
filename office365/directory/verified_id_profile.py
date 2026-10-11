from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.identities.providers.verified_id_profile_state import (
        VerifiedIdProfileState,
    )
    from office365.directory.policies.face_check_configuration import (
        FaceCheckConfiguration,
    )
    from office365.directory.policies.verified_id_profile_configuration import (
        VerifiedIdProfileConfiguration,
    )
    from office365.directory.policies.verified_id_usage_configuration import (
        VerifiedIdUsageConfiguration,
    )


class VerifiedIdProfile(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def face_check_configuration(self) -> FaceCheckConfiguration:
        """Gets the faceCheckConfiguration property"""
        from office365.directory.policies.face_check_configuration import (
            FaceCheckConfiguration,
        )

        return self.properties.get("faceCheckConfiguration", FaceCheckConfiguration())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def priority(self) -> Optional[int]:
        """Gets the priority property"""
        return self.properties.get("priority", None)

    @property
    def state(self) -> VerifiedIdProfileState:
        """Gets the state property"""
        from office365.directory.identities.providers.verified_id_profile_state import (
            VerifiedIdProfileState,
        )

        return self.properties.get("state", VerifiedIdProfileState.enabled)

    @property
    def verified_id_profile_configuration(self) -> VerifiedIdProfileConfiguration:
        """Gets the verifiedIdProfileConfiguration property"""
        from office365.directory.policies.verified_id_profile_configuration import (
            VerifiedIdProfileConfiguration,
        )

        return self.properties.get("verifiedIdProfileConfiguration", VerifiedIdProfileConfiguration())

    @property
    def verified_id_usage_configurations(self) -> ClientValueCollection[VerifiedIdUsageConfiguration]:
        """Gets the verifiedIdUsageConfigurations property"""
        from office365.directory.policies.verified_id_usage_configuration import (
            VerifiedIdUsageConfiguration,
        )

        return self.properties.get(
            "verifiedIdUsageConfigurations",
            ClientValueCollection[VerifiedIdUsageConfiguration](VerifiedIdUsageConfiguration),
        )

    @property
    def verifier_did(self) -> Optional[str]:
        """Gets the verifierDid property"""
        return self.properties.get("verifierDid", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VerifiedIdProfile"
