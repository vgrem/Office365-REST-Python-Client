from enum import Enum


class AdditionalDataOptions(Enum):
    allVersions = "1"
    linkedFiles = "2"
    unknownFutureValue = "4"
    advancedIndexing = "8"
    listAttachments = "16"
    htmlTranscripts = "32"
    messageConversationExpansion = "64"
    locationsWithoutHits = "256"
    allItemsInFolder = "512"
    cloudNativeHtmlConversion = "1024"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.AdditionalDataOptions"
