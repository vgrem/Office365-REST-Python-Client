from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from office365.runtime.client_value import ClientValue


@dataclass
class ContentTypeId(ClientValue):
    """
    The ContentTypeId type is the identifier for the specified content type. The identifier is a string of
    hexadecimal characters. The identifier MUST be unique relative to the current site collection and site and MUST
    follow the pattern of prefixing a ContentTypeId with its parent ContentTypeId.

    ContentTypeId MUST follow the XSD pattern specified in [MS-WSSCAML] section 2.3.1.4.
    """

    StringValue: Optional[str] = None

    @property
    def entity_type_name(self) -> str:
        return "SP.ContentTypeId"

    def __repr__(self) -> str:
        return str(self.StringValue or self.entity_type_name)
