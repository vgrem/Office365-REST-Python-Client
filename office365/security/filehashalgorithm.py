from enum import Enum


class FileHashAlgorithm(Enum):
    unknown = "0"
    md5 = "1"
    sha1 = "2"
    sha256 = "3"
    sha256ac = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.FileHashAlgorithm"
