from enum import Enum


class UserActivityTypes(Enum):
    none = "0"
    uploadText = "1"
    uploadFile = "2"
    downloadText = "4"
    downloadFile = "8"
    unknownFutureValue = "16"
    copyToClipboard = "32"
    pasteFromClipboard = "64"
    print = "128"
    accessDebugTools = "256"

    @property
    def entity_type_name(self):
        return "microsoft.graph.UserActivityTypes"
