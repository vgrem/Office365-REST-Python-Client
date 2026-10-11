from enum import Enum


class ExportOptions(Enum):
    originalFiles = "1"
    text = "2"
    pdfReplacement = "4"
    tags = "16"
    unknownFutureValue = "32"
    splitSource = "64"
    includeFolderAndPath = "128"
    friendlyName = "256"
    condensePaths = "512"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ExportOptions"
