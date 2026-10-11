from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.identitygovernance.entitlementmanagement.custom_extension_overwrite_configuration import (
    CustomExtensionOverwriteConfiguration,
)
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.common.on_attribute_collection_submit_custom_extension import (
        OnAttributeCollectionSubmitCustomExtension,
    )


@dataclass
class OnAttributeCollectionSubmitCustomExtensionHandler(ClientValue):
    configuration: CustomExtensionOverwriteConfiguration = field(default_factory=CustomExtensionOverwriteConfiguration)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnAttributeCollectionSubmitCustomExtensionHandler"

    customExtension: OnAttributeCollectionSubmitCustomExtension | None = None
