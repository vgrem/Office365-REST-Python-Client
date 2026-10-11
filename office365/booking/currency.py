from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class BookingCurrency(Entity):
    """Represents a monetary currency supported by a bookingBusiness."""

    @property
    def symbol(self) -> Optional[str]:
        """Gets the symbol property"""
        return self.properties.get("symbol", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingCurrency"
