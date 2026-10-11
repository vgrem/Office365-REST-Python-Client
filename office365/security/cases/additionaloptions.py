from enum import Enum


class AdditionalOptions(Enum):
    none = "0"
    teamsAndYammerConversations = "1"
    cloudAttachments = "2"
    allDocumentVersions = "4"
    subfolderContents = "8"
    listAttachments = "16"
    unknownFutureValue = "32"
    htmlTranscripts = "64"
    advancedIndexing = "128"
    allItemsInFolder = "256"
    includeFolderAndPath = "512"
    condensePaths = "1024"
    friendlyName = "2048"
    splitSource = "4096"
    includeReport = "16384"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.AdditionalOptions"
