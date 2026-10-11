from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.qr_code import QrCode
    from office365.common.qr_pin import QrPin


class QrCodePinAuthenticationMethod(Entity):
    @property
    def pin(self) -> QrPin:
        """Gets the pin property"""
        from office365.common.qr_pin import QrPin

        return self.properties.get("pin", QrPin(self.context, ResourcePath("pin", self.resource_path)))

    @property
    def standard_qr_code(self) -> QrCode:
        """Gets the standardQRCode property"""
        from office365.common.qr_code import QrCode

        return self.properties.get(
            "standardQRCode", QrCode(self.context, ResourcePath("standardQRCode", self.resource_path))
        )

    @property
    def temporary_qr_code(self) -> QrCode:
        """Gets the temporaryQRCode property"""
        from office365.common.qr_code import QrCode

        return self.properties.get(
            "temporaryQRCode", QrCode(self.context, ResourcePath("temporaryQRCode", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.QrCodePinAuthenticationMethod"
