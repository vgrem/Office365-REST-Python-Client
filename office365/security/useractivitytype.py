from enum import Enum


class UserActivityType(Enum):
    uploadText = "1"
    uploadFile = "2"
    downloadText = "3"
    downloadFile = "4"
    unknownFutureValue = "5"
    copyToClipboard = "6"
    pasteFromClipboard = "7"
    print = "8"
    accessDebugTools = "9"

    @property
    def entity_type_name(self):
        return "microsoft.graph.UserActivityType"
