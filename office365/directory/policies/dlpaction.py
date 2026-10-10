from __future__ import annotations

from enum import Enum


class DlpAction(Enum):
    notifyUser = "0"
    blockAccess = "1"
    deviceRestriction = "2"
    browserRestriction = "3"
    unknownFutureValue = "4"
    restrictAccess = "5"
    generateAlert = "6"
    generateIncidentReportAction = "7"
    sPBlockAnonymousAccess = "8"
    sPRuntimeAccessControl = "9"
    sPSharingNotifyUser = "10"
    sPSharingGenerateIncidentReport = "11"
    restrictWebGrounding = "12"

    @property
    def entity_type_name(self):
        return "microsoft.graph.DlpAction"

    policyTip = "13"
