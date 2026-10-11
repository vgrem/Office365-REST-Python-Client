from enum import Enum


class CaseAction(Enum):
    contentExport = "0"
    applyTags = "1"
    convertToPdf = "2"
    index = "3"
    estimateStatistics = "4"
    addToReviewSet = "5"
    holdUpdate = "6"
    unknownFutureValue = "7"
    purgeData = "8"
    exportReport = "9"
    exportResult = "10"
    holdPolicySync = "11"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.CaseAction"
