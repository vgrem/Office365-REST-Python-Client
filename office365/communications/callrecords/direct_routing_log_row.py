from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class DirectRoutingLogRow(ClientValue):
    """Represents a row of data in the direct routing call log. Each row maps to one call."""
