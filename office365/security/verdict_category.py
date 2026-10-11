from __future__ import annotations

from enum import Enum


class VerdictCategory(Enum):
    none = "0"
    malware = "1"
    phish = "2"
    siteUnavailable = "3"
    spam = "4"
    decryptionFailed = "5"
    unsupportedUriScheme = "6"
    unsupportedFileType = "7"
    undefined = "8"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.VerdictCategory"
